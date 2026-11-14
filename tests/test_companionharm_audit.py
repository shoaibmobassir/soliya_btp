"""Exercise the audit on independently authored temporary CSV files."""

from contextlib import redirect_stderr, redirect_stdout
import csv
import hashlib
from io import StringIO
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from scripts import audit_companionharm as audit


def row(split, conversation, target, **changes):
    return {
        "utterance_id": f"{conversation}::2",
        "conversation_id": conversation,
        "line_number": "2",
        "speaker": "Replika",
        "context": "",
        "current_line": target,
        "label": "No harmful behavior",
        "agreement_type": "3-way agreement",
        "majority_vote_count": "3",
        "annotator_count": "3",
        "split": split,
        **changes,
    }


class CompanionHarmAuditTests(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.source = {"id": "companionharm", "revision": "0" * 40, "data_objects": []}

    def write_split(self, split, rows):
        path = self.directory / f"{split}.csv"
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        payload = path.read_bytes()
        expected = {
            "path": f"data/splits/{path.name}",
            "reported_bytes": len(payload),
            "git_blob_oid": hashlib.sha1(f"blob {len(payload)}\0".encode() + payload).hexdigest(),
            "reported_rows": len(rows),
            "reported_conversations": len({record["conversation_id"] for record in rows}),
        }
        self.source["data_objects"].append(expected)
        return path, expected

    def run_cli(self):
        manifest = self.directory / "manifest.json"
        manifest.write_text(json.dumps({"sources": [self.source]}), encoding="utf-8")
        output, errors = StringIO(), StringIO()
        with patch.object(audit, "MANIFEST", manifest):
            with redirect_stdout(output), redirect_stderr(errors):
                status = audit.main(["--split-dir", str(self.directory)])
        return status, output.getvalue(), errors.getvalue()

    def test_checks_pinned_bytes_without_modifying_sources_or_exporting_records(self):
        train, _ = self.write_split("train", [row("train", "fixture-group-A", "fixture text A")])
        self.write_split("dev", [row("dev", "fixture-group-B", "fixture text B", label="Control")])
        self.write_split("test", [row("test", "fixture-group-C", "fixture text C")])
        before = train.read_bytes()

        status, output, errors = self.run_cli()
        self.assertEqual(status, 0)
        self.assertEqual(errors, "")
        report = json.loads(output)
        self.assertFalse(report["blocking_integrity_findings"])
        self.assertEqual(report["splits"]["train"]["source_sha256"], hashlib.sha256(before).hexdigest())
        self.assertEqual(report["splits"]["train"]["blank_context_by_turn"], {"2": 1})
        self.assertEqual(report["splits"]["dev"]["harmful_rows"], 1)
        self.assertEqual(report["cross_split_intersections"]["train-test"]["conversation_ids"], 0)
        self.assertIn("fuzzy_conversation_overlap", report["pending_checks"])
        self.assertNotIn("fixture-group", output)
        self.assertNotIn("fixture text", output)
        self.assertEqual(train.read_bytes(), before)

    def test_detects_duplicates_split_overlap_and_unresolved_labels(self):
        train_row = row("train", "group-A", "café", context="café")
        self.write_split("train", [train_row, train_row])
        self.write_split("dev", [row("dev", "group-A", "cafe\u0301", context="cafe\u0301")])
        self.write_split("test", [
            row("test", "group-C", "other", label="Others", majority_vote_count="1"),
        ])

        status, output, errors = self.run_cli()
        report = json.loads(output)
        self.assertEqual((status, errors), (1, ""))
        self.assertEqual(report["splits"]["train"]["duplicate_rows"], 1)
        self.assertEqual(report["splits"]["train"]["duplicate_utterance_ids"], 1)
        self.assertEqual(report["splits"]["train"]["exact_target_context_rows"], 2)
        self.assertEqual(report["splits"]["test"]["unresolved_agreement_rows"], 1)
        self.assertEqual(report["splits"]["test"]["invalid_label_rows"], 1)
        self.assertEqual(report["cross_split_intersections"]["train-dev"], {
            "conversation_ids": 1, "utterance_ids": 1, "normalized_context_target_pairs": 1,
        })

    def test_rejects_wrong_blob_without_partial_output(self):
        path, _ = self.write_split("train", [row("train", "group-A", "before")])
        path.write_bytes(path.read_bytes().replace(b"before", b"edited"))
        status, output, errors = self.run_cli()
        self.assertEqual((status, output), (2, ""))
        self.assertEqual(json.loads(errors), {"error": "split_bytes_do_not_match_pinned_release"})

    def test_malformed_header_is_not_exposed(self):
        self.write_split("train", [row("train", "group-A", "before", sentinel_private_field="hidden")])
        status, output, errors = self.run_cli()
        self.assertEqual((status, output), (2, ""))
        self.assertEqual(json.loads(errors), {"error": "unexpected_split_header"})

    def test_detects_changed_bytes_after_parsing(self):
        path, expected = self.write_split("train", [row("train", "group-A", "before")])
        payload = path.read_bytes()
        with patch.object(Path, "read_bytes", side_effect=[payload, payload + b"\n"]):
            with self.assertRaisesRegex(audit.AuditError, "split_changed_during_audit"):
                audit.audit_split(path, "train", expected)

    def test_binary_mapping_has_closed_label_set(self):
        self.assertEqual(len(audit.LABELS), 14)
        for label in audit.LABELS:
            expected = "safe" if label == "No harmful behavior" else "harmful"
            self.assertEqual(audit.binary_label(label), expected)
        self.assertIsNone(audit.binary_label("Others"))
        self.assertIsNone(audit.binary_label(""))

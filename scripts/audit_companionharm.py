"""Audit a pinned CompanionHarm release locally and report aggregate counts."""

import argparse
from collections import Counter
import csv
import hashlib
import io
from itertools import combinations
import json
from pathlib import Path
import re
import sys
import unicodedata


SPLITS = ("train", "dev", "test")
FIELDS = {
    "utterance_id", "conversation_id", "line_number", "speaker", "context",
    "current_line", "label", "agreement_type", "majority_vote_count",
    "annotator_count", "split",
}
LABELS = frozenset({
    "Antisocial behavior", "Hate speech", "Control", "Disregard", "Infidelity",
    "Manipulation", "Mis/Disinformation", "No harmful behavior",
    "Physical aggression", "Privacy violations", "Self-harm & Suicide",
    "Sexual misconduct", "Substance abuse", "Verbal abuse",
})
AGREEMENT_TYPES = {"2": "2-way agreement", "3": "3-way agreement"}
MANIFEST = Path(__file__).resolve().parents[1] / "data" / "source_manifest.json"


class AuditError(Exception):
    """A fixed diagnostic safe to include in an audit log."""


def normalize_text(value):
    return " ".join(unicodedata.normalize("NFC", value).split())


def binary_label(label):
    if label not in LABELS:
        return None
    return "safe" if label == "No harmful behavior" else "harmful"


def read_pinned_split(path, expected):
    payload = path.read_bytes()
    header = f"blob {len(payload)}\0".encode("ascii")
    object_id = hashlib.sha1(header + payload).hexdigest()
    if len(payload) != expected["reported_bytes"] or object_id != expected["git_blob_oid"]:
        raise AuditError("split_bytes_do_not_match_pinned_release")
    return payload


def audit_split(path, split, expected):
    payload = read_pinned_split(path, expected)
    digest = hashlib.sha256(payload).hexdigest()
    counts = Counter({
        "rows": 0, "duplicate_rows": 0, "duplicate_utterance_ids": 0,
        "invalid_metadata_rows": 0, "unresolved_agreement_rows": 0,
        "invalid_label_rows": 0, "safe_rows": 0, "harmful_rows": 0,
        "blank_context_rows": 0, "empty_target_rows": 0,
        "exact_target_context_rows": 0, "normalized_target_substring_rows": 0,
    })
    blank_context_by_turn = Counter()
    conversations, utterances, rows, text_pairs = set(), set(), set(), set()
    with io.TextIOWrapper(io.BytesIO(payload), encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, strict=True)
        headers = reader.fieldnames or []
        if len(headers) != len(FIELDS) or set(headers) != FIELDS:
            raise AuditError("unexpected_split_header")
        for row in reader:
            if None in row or any(value is None for value in row.values()):
                raise AuditError("malformed_split_row")
            counts["rows"] += 1
            utterance = row["utterance_id"]
            conversation = row["conversation_id"]
            turn = row["line_number"]
            turn_is_valid = re.fullmatch(r"[0-9]{1,9}", turn) is not None
            counts["invalid_metadata_rows"] += (
                not utterance.strip() or not conversation.strip() or not turn_is_valid
                or row["speaker"] != "Replika" or row["split"] != split
            )
            values = tuple(row.values())
            counts["duplicate_rows"] += values in rows
            counts["duplicate_utterance_ids"] += bool(utterance) and utterance in utterances
            rows.add(values)
            if utterance.strip():
                utterances.add(utterance)
            if conversation.strip():
                conversations.add(conversation)

            label = binary_label(row["label"])
            resolved = (
                row["annotator_count"] == "3"
                and row["agreement_type"] == AGREEMENT_TYPES.get(row["majority_vote_count"])
            )
            counts["unresolved_agreement_rows"] += not resolved
            counts["invalid_label_rows"] += label is None
            if resolved and label is not None:
                counts[f"{label}_rows"] += 1

            context = normalize_text(row["context"])
            target = normalize_text(row["current_line"])
            counts["blank_context_rows"] += not context
            counts["empty_target_rows"] += not target
            if not context and turn_is_valid:
                blank_context_by_turn[int(turn)] += 1
            if context and target:
                text_pairs.add((context, target))
                counts["exact_target_context_rows"] += row["context"] == row["current_line"]
                counts["normalized_target_substring_rows"] += target in context

    if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise AuditError("split_changed_during_audit")
    counts["conversations"] = len(conversations)
    counts["count_mismatch"] = (
        counts["rows"] != expected["reported_rows"]
        or counts["conversations"] != expected["reported_conversations"]
    )
    summary = dict(counts, source_sha256=digest, blank_context_by_turn=dict(blank_context_by_turn))
    return summary, conversations, utterances, text_pairs


def audit_splits(split_dir, source):
    objects = {obj["path"]: obj for obj in source["data_objects"]}
    summaries, conversation_keys, utterance_keys, text_pairs = {}, {}, {}, {}
    for split in SPLITS:
        filename = f"{split}.csv"
        summaries[split], conversation_keys[split], utterance_keys[split], text_pairs[split] = (
            audit_split(split_dir / filename, split, objects[f"data/splits/{filename}"])
        )

    intersections = {}
    for left, right in combinations(SPLITS, 2):
        intersections[f"{left}-{right}"] = {
            "conversation_ids": len(conversation_keys[left] & conversation_keys[right]),
            "utterance_ids": len(utterance_keys[left] & utterance_keys[right]),
            "normalized_context_target_pairs": len(text_pairs[left] & text_pairs[right]),
        }
    hard_findings = (
        "count_mismatch", "duplicate_rows", "duplicate_utterance_ids",
        "invalid_metadata_rows", "unresolved_agreement_rows",
        "invalid_label_rows", "empty_target_rows",
    )
    blocking = any(summary[key] for summary in summaries.values() for key in hard_findings)
    blocking |= any(pair["conversation_ids"] or pair["utterance_ids"] for pair in intersections.values())
    return {
        "source_revision": source["revision"],
        "blocking_integrity_findings": blocking,
        "splits": summaries,
        "cross_split_intersections": intersections,
        "pending_checks": [
            "classify_exact_text_overlap_and_target_repetition",
            "parse_context_roles_turns_and_detect_post_target_leakage",
            "fuzzy_conversation_overlap",
            "prior_holdout_exposure",
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split-dir", required=True, type=Path, help="Approved local split directory")
    args = parser.parse_args(argv)
    try:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        source = next(source for source in manifest["sources"] if source["id"] == "companionharm")
        report = audit_splits(args.split_dir, source)
    except AuditError as error:
        print(json.dumps({"error": str(error)}), file=sys.stderr)
        return 2
    except (OSError, UnicodeError, csv.Error, ValueError, KeyError, TypeError, StopIteration):
        print(json.dumps({"error": "cannot_read_or_parse_audit_input"}), file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return int(report["blocking_integrity_findings"])


if __name__ == "__main__":
    sys.exit(main())

import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.development_data import Reply
from scripts.prepare_blind_pilot import assign, candidate_arms, check_approval, valid_structure


class BlindPilotTests(unittest.TestCase):
    def test_packet_preparation_requires_recorded_approval(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "approval.json"
            with self.assertRaises(ValueError):
                check_approval(path, "ref")
            path.write_text(json.dumps({"status": "approved", "reference": "ref",
                                        "approved_by": "reviewer", "approved_on": "2026-11-13"}))
            check_approval(path, "ref")
            with self.assertRaises(ValueError):
                check_approval(path, "wrong-ref")

    def test_preserve_focal_reply_and_blind_condition_identity(self):
        target = "Replika: Welcome, Blue."
        source = Reply("reply", "group", (("User", "Call me Blue."),), "User: Call me Blue.",
                       target, 0, "example", 3)
        entry = {
            "anchor_id": "private_anchor", "source_conversation_id": "group",
            "target": target, "original_prefix": source.raw_context,
            "target_sha256": hashlib.sha256(target.encode()).hexdigest(),
            "screening_status": "eligible",
            "edits": {
                "intended_change": {"prefix": "User: Stop calling me Blue.", "family": "boundary",
                                    "status": "constructed", "decision": "modify"},
                "intended_preserve": {"prefix": "User: Call me Blue, please.", "family": "boundary",
                                      "status": "constructed", "decision": "modify"},
            },
        }
        arms = candidate_arms(entry, source)
        ids = iter(("q1", "q2", "q3"))
        packets, key = assign([(entry, target, arms)], [f"r{i}" for i in range(9)],
                              condition_id=lambda: next(ids))
        self.assertEqual(len(key), 3)
        self.assertTrue(all(len(items) == 1 for items in packets.values()))
        for items in packets.values():
            self.assertEqual(set(items[0]), {"condition_id", "turns", "target"})
            self.assertEqual(items[0]["target"], target)
        with self.assertRaises(ValueError):
            candidate_arms({**entry, "target": "changed"}, source)
        entry["edits"]["intended_preserve"]["prefix"] = "Replika: Call me Blue."
        with self.assertRaises(ValueError):
            candidate_arms(entry, source)

    def test_family_contracts_allow_distractor_insertion_and_moved_evidence(self):
        original = (("User", "A"), ("Replika", "B"), ("User", "C"))
        inserted = (*original, ("User", "Unrelated detail"))
        moved = (original[1], original[0], original[2])
        self.assertTrue(valid_structure(original, inserted, "irrelevant_distractor"))
        self.assertTrue(valid_structure(original, moved, "evidence_distance"))
        self.assertFalse(valid_structure(original, inserted, "boundary"))
        with self.assertRaises(ValueError):
            assign([({"source_conversation_id": "source"}, "reply",
                     dict.fromkeys(("original", "edit_a", "edit_b", "target_only")))],
                   [f"r{i}" for i in range(9)])

import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.development_data import Reply
from scripts.pilot_screening_status import summarize


class ScreeningStatusTests(unittest.TestCase):
    def test_pending_and_ineligible_never_become_validated_labels(self):
        target = "Replika: Hello."
        source = Reply("r", "c", (("User", "Hi"),), "User: Hi", target, 0, "safe", 3)
        row = {"source_utterance_id": "r", "source_conversation_id": "c",
               "target": target, "original_prefix": source.raw_context,
               "target_sha256": hashlib.sha256(target.encode()).hexdigest(),
               "screening_status": "ineligible", "screening_reason": "privacy"}
        with TemporaryDirectory() as directory:
            report = summarize([row], {"r": source}, Path(directory) / "approval.json")
        self.assertEqual(report["counts"]["screened"], 1)
        self.assertEqual(report["rejection_and_impossibility_reasons"], {"privacy": 1})
        self.assertEqual(report["go_no_go"], "pending_independent_human_validation")
        self.assertFalse(report["independent_review_plan_approved"])

import hashlib
import unittest

from scripts.development_data import Reply
from scripts.edit_pilot_case import author_view, validate_revision


class PilotEditorTests(unittest.TestCase):
    def test_complete_available_conversation_and_label_are_visible(self):
        first = Reply("r1", "c", (), "", "Replika: Hello.", 0, "safe", 3)
        later = Reply("r2", "c", (("Replika", "Hello."), ("User", "Hi")),
                      "Replika: Hello.\nUser: Hi", "Replika: Welcome.", 0, "safe", 3)
        entry = {"source_conversation_id": "c", "target": first.target,
                 "upstream_category": "safe", "model_suggestions": {"candidate": {}}}
        view = author_view(entry, [first, later])
        self.assertEqual(len(view["turns"]), 3)
        self.assertEqual(view["focal_reply"], first.target)
        self.assertEqual(view["original_annotation_category"], "safe")
        self.assertEqual(view["candidate_suggestions"], entry["model_suggestions"])

    def test_source_and_model_suggestions_cannot_be_altered(self):
        target = "Replika: Hello."
        source = Reply("r", "c", (("User", "Hi"),), "User: Hi", target, 0, "safe", 3)
        item = {"anchor_id": "P001", "source_conversation_id": "c", "source_utterance_id": "r",
                "original_prefix": source.raw_context, "target": target,
                "target_sha256": hashlib.sha256(target.encode()).hexdigest(),
                "screening_status": "pending", "model_suggestions": {}}
        validate_revision(item, dict(item), {"r": source})
        with self.assertRaises(ValueError):
            validate_revision(item, {**item, "target": "changed"}, {"r": source})
        with self.assertRaises(ValueError):
            validate_revision(item, {**item, "model_suggestions": {"edited": True}}, {"r": source})

import unittest

from scripts.draft_pilot_locally import parse_proposal


class PilotDraftTests(unittest.TestCase):
    def test_requires_one_numbered_user_turn_and_never_accepts_the_draft(self):
        turns = (("User", "Please call me Blue."), ("Replika", "All right."),
                 ("User", "The window is open."))
        draft = parse_proposal(
            '{"change":{"turn":1,"text":"Do not call me Blue."},'
            '"preserve":{"turn":2,"text":"The door is open."}}', turns,
        )
        self.assertEqual(draft["change"]["status"], "needs_author_review")
        self.assertIn("Replika: All right.", draft["change"]["prefix"])
        self.assertIsNone(draft["preserve"])
        with self.assertRaises(ValueError):
            parse_proposal('{"change":null}', turns)

import unittest

from scripts.summarize_human_pilot import summarize


class HumanPilotTests(unittest.TestCase):
    def test_human_labels_determine_observed_relations(self):
        cases = [
            ("original", "A", "no_boundary_violation", "no_harm"),
            ("intended_change", "B", "no_boundary_violation", "harmful"),
            ("intended_preserve", "C", "boundary_violation", "undetermined"),
        ]
        coordinator, ratings, adjudication = [], [], []
        for arm, key, boundary, harmfulness in cases:
            reviewers = [f"{key}{i}" for i in range(3)]
            coordinator.append({"condition_id": key, "anchor_id": "one", "arm": arm,
                                "reviewers": reviewers})
            labels = {"condition_id": key, "boundary_label": boundary, "harmfulness_label": harmfulness}
            ratings.extend({**labels, "reviewer_id": code} for code in reviewers)
            adjudication.append({**labels, "reviewer_id": "judge", "reason": "fixture"})
        quality = [{"condition_id": key, "accepted": True, "reviewer_id": "quality", "reason": "fixture"}
                   for key in ("B", "C")]
        result = summarize(coordinator, ratings, adjudication, quality)
        boundary = result["rubrics"]["boundary"]["intended_to_observed"]
        harmfulness = result["rubrics"]["harmfulness"]["intended_to_observed"]
        self.assertEqual(boundary["intended_change_observed_preserve"], 1)
        self.assertEqual(boundary["intended_preserve_observed_change"], 1)
        self.assertEqual(harmfulness["intended_change_observed_change"], 1)
        self.assertEqual(harmfulness["intended_preserve_observed_undetermined"], 1)
        with self.assertRaises(ValueError):
            summarize(coordinator, ratings[:-1], adjudication, quality)
        with self.assertRaises(ValueError):
            summarize(coordinator, ratings, [{**adjudication[0], "reviewer_id": "A0"},
                                              *adjudication[1:]], quality)

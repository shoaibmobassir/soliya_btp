import unittest

from scripts.paired_metrics import Pair, evaluate


class PairedMetricsTests(unittest.TestCase):
    def test_stability_and_correct_adaptation_are_distinct(self):
        safe = "no_boundary_violation"
        harm = "boundary_violation"
        pairs = [Pair("one", "a", "b", True), Pair("one", "a", "c", True),
                 Pair("two", "d", "e", False), Pair("two", "d", "f", True)]
        gold = {"a": safe, "b": safe, "c": harm, "d": safe, "e": harm, "f": "undetermined"}
        oracle = {"a": safe, "b": safe, "c": harm}
        constant = {key: safe for key in oracle}
        swapped = {"a": harm, "b": harm, "c": safe}
        report = evaluate(pairs, gold, {"oracle": oracle, "constant": constant, "swapped": swapped},
                          reps=20, contrast=("oracle", "constant"))
        self.assertEqual(report["eligible_pairs"], 2)
        self.assertEqual(report["conversations"], 1)
        self.assertEqual(report["models"]["oracle"]["ufr"]["estimate"], 0)
        self.assertEqual(report["models"]["constant"]["ufr"]["estimate"], 0)
        self.assertEqual(report["models"]["oracle"]["ccar"]["estimate"], 1)
        self.assertEqual(report["models"]["constant"]["ccar"]["estimate"], 0)
        self.assertEqual(report["models"]["swapped"]["ccar"]["estimate"], 0)
        self.assertEqual(report["contrast"]["ccar"]["estimate"], 1)
        self.assertIsNone(report["contrast"]["ccar"]["interval"])

    def test_empty_relation_stays_undefined_and_eligible_predictions_are_required(self):
        safe = "no_boundary_violation"
        pair = Pair("one", "a", "b", True)
        gold = {"a": safe, "b": safe}
        self.assertIsNone(evaluate([pair], gold, {"x": gold}, reps=5)["models"]["x"]["ccar"]["estimate"])
        with self.assertRaises(ValueError):
            evaluate([pair], gold, {"x": {"a": safe}}, reps=5)
        with self.assertRaises(ValueError):
            evaluate([Pair("one", "a", "b", "false")], gold, {"x": gold}, reps=5)

    def test_unequal_conversation_sizes_use_pair_weighted_point_estimate(self):
        safe = "no_boundary_violation"
        harm = "boundary_violation"
        pairs = [Pair("short", "a", "b", True), Pair("long", "c", "d", True),
                 Pair("long", "c", "e", True), Pair("long", "c", "f", True)]
        gold = dict.fromkeys("abcdef", safe)
        predictions = {**gold, "d": harm, "e": harm, "f": harm}
        report = evaluate(pairs, gold, {"x": predictions, "copy": predictions},
                          reps=40, contrast=("x", "copy"))
        self.assertEqual(report["models"]["x"]["ufr"]["estimate"], 0.75)
        self.assertEqual(report["contrast"]["ufr"]["interval"], [0, 0])

import csv
import io
import unittest

from scripts.audit_conversation_overlap import match_traces, reconstruct_split


class ConversationOverlapTests(unittest.TestCase):
    def test_reconstruction_uses_one_speaker_marker_per_turn(self):
        stream = io.StringIO()
        writer = csv.writer(stream)
        writer.writerow(("conversation_id", "line_number", "context", "current_line"))
        writer.writerow(("source", 1, "", "Replika: Good morning."))
        writer.writerow(("source", 3, "Replika: Good morning.\nUser: Hello.", "Replika: Good morning."))
        summary, traces = reconstruct_split(stream.getvalue().encode())
        self.assertEqual(summary["prefix_consistency_mismatches"], 0)
        self.assertEqual(summary["exact_target_at_earlier_ai_turn"], 1)
        self.assertEqual(traces, {
            "source": (("Replika", "Good morning."), ("User", "Hello."), ("Replika", "Good morning.")),
        })

    def test_near_matches_exclude_exact_trace_pairs(self):
        trace = (("User", "one two three four five six seven eight nine ten eleven twelve"),)
        similar = (("User", trace[0][1] + " thirteen"),)
        unrelated = (("Replika", "red orange yellow green blue violet white black"),)
        self.assertEqual(
            match_traces({"source": trace}, {"copy": trace, "variant": similar, "other": unrelated}),
            {"exact": {("source", "copy")}, "near": {("source", "variant")}},
        )

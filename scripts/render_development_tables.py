"""Render exploratory development tables from the saved run aggregate."""

import json

from scripts.development_data import ROOT
from scripts.render_audit_tables import table


def formatted(stat):
    estimate = stat["estimate"]
    low, high = stat["interval"]
    return f"{estimate:.3f} [{low:.3f}, {high:.3f}]"


def main():
    report = json.loads((ROOT / "results/CONTEXT_AUDIT_DEV.json").read_text())
    metrics = ("macro_f1", "harmful_recall", "safe_fpr")
    classification = [
        ("Input", "Macro-F1", "Harmful recall", "Safe FPR"),
        *((label, *(formatted(report["natural_input_metrics"][key][metric]) for metric in metrics))
          for key, label in (("target_model", "Reply only"), ("full", "Full prefix"))),
        ("Full minus reply", *(formatted(report["full_minus_target"][metric]) for metric in metrics)),
    ]
    probes = [("Probe", "Rows", "Input changed", "Flips", "Rate [95\\% interval]")]
    for key, label in (
        ("removed", "Remove prefix"), ("last_user", "Last user turn"), ("last_three", "Last three turns"),
        ("shuffled", "Shuffle order"), ("mismatched_length", "Length-matched donor"),
        ("neutral_padding", "Append neutral padding"), ("neutral_replacement", "Replace with neutral text"),
        ("user_only", "User turns only"), ("prior_ai_only", "Earlier AI turns only"),
    ):
        stat = report["unvalidated_probe_flip_rates"][key]
        probes.append((label, stat["rows"], stat["rows_with_changed_rendering"], stat["flips"], formatted(stat)))
    output = "\n\n".join((
        table("lrrr", "Exploratory development estimates with conversation-clustered 95\\% intervals. "
              "Each native input has its own trained model.", classification),
        table("lrrrr", "Prediction changes relative to the fixed full-prefix model. Denominators cover "
              "available probes with nonempty original prefixes.", probes),
    ))
    (ROOT / "paper/development_tables.tex").write_text(output + "\n")


if __name__ == "__main__":
    main()

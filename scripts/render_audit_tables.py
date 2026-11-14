"""Render the paper's audit tables from aggregate CompanionHarm results."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def table(columns, caption, rows):
    body = [r" & ".join(map(str, row)) + r" \\" for row in rows]
    return "\n".join([
        r"\begin{table}[htbp]", r"\centering", r"\caption{" + caption + "}",
        r"\begin{tabular}{" + columns + "}", r"\toprule",
        body[0], r"\midrule", *body[1:], r"\bottomrule",
        r"\end{tabular}", r"\end{table}",
    ])


def main():
    data = json.loads((ROOT / "results/COMPANIONHARM_AUDIT.json").read_text())
    splits = data["integrity"]["splits"]
    intersections = data["integrity"]["cross_split_intersections"]
    traces = data["cross_split_trace_pairs"]
    split_rows = [
        ("Split", "Replies", "Conversation IDs", "Blank prefixes"),
        *((name, f"{splits[key]['rows']:,}", f"{splits[key]['conversations']:,}",
           f"{splits[key]['blank_context_rows']:,}")
          for key, name in (("train", "Train"), ("dev", "Development"), ("test", "Test"))),
    ]
    overlap_rows = [
        ("Split comparison", "Context--reply matches", "Exact traces", "Near traces"),
        *((name, intersections[key]["normalized_context_target_pairs"],
           traces[key]["exact_trace_pairs"], traces[key]["near_trace_pairs"])
          for key, name in (("train-dev", "Train--development"),
                            ("train-test", "Train--test"), ("dev-test", "Development--test"))),
    ]
    tables = [
        table("lrrr", "Observed counts for the pinned CompanionHarm splits.", split_rows),
        table("lrrr", "Cross-split matches after normalization. Trace counts count pairs of "
              "conversation IDs. Near traces exclude exact traces.", overlap_rows),
    ]
    (ROOT / "paper/audit_tables.tex").write_text("\n\n".join(tables) + "\n")


if __name__ == "__main__":
    main()

"""Summarize local human screening without exporting case text or identifiers."""

from collections import Counter
import json
from pathlib import Path

from scripts.development_data import ROOT, load_development
from scripts.edit_pilot_case import read_queue
from scripts.prepare_blind_pilot import candidate_arms, check_approval


REASONS = {"privacy", "insufficient_context", "no_boundary", "incoherent",
           "out_of_scope", "no_valid_edit", "duplicate", "other"}


def summarize(rows, sources, approval_path, human_report=None):
    counts = Counter({"screened": 0, "eligible": 0, "ineligible": 0,
                      "pending": 0, "invalid": 0, "constructed_edits": 0,
                      "rejected_edits": 0, "impossible_edits": 0})
    reasons = Counter()
    decisions = Counter()
    for row in rows:
        if row.get("screening_status") == "pending":
            counts["pending"] += 1
            continue
        try:
            source = sources[row["source_utterance_id"]]
            arms = candidate_arms(row, source)
        except (KeyError, ValueError, TypeError):
            counts["invalid"] += 1
            continue
        counts["screened"] += 1
        if not arms:
            counts["ineligible"] += 1
            reason = row.get("screening_reason")
            reasons[reason if reason in REASONS else "other"] += 1
            continue
        counts["eligible"] += 1
        for edit in row["edits"].values():
            status = edit["status"]
            if status == "constructed":
                counts["constructed_edits"] += 1
                decisions[edit["decision"]] += 1
            elif status == "rejected":
                counts["rejected_edits"] += 1
                reason = edit.get("reason")
                reasons[reason if reason in REASONS else "other"] += 1
            elif status == "not_constructible":
                counts["impossible_edits"] += 1
                reason = edit.get("reason")
                reasons[reason if reason in REASONS else "other"] += 1
    approved = False
    if approval_path.exists():
        try:
            data = json.loads(approval_path.read_text())
            check_approval(approval_path, data.get("reference"))
            approved = True
        except (OSError, ValueError, TypeError):
            pass
    done = counts["screened"] == len(rows) and not counts["invalid"]
    return {
        "total_sources": len(rows), "counts": dict(counts), "author_decisions": dict(decisions),
        "rejection_and_impossibility_reasons": dict(reasons),
        "screening_complete": done, "independent_review_plan_approved": approved,
        "independent_human_evidence": "available" if human_report else "not_available",
        "go_no_go": "requires_human_feasibility_and_precision_review" if human_report
                    else "pending_independent_human_validation",
    }


def main():
    private = ROOT / "private_data/boundary_pilot"
    _, rows = read_queue(private / "review_drafts.jsonl")
    data, _ = load_development()
    sources = {row.utterance: row for row in data["dev"]}
    human_path = ROOT / "results/PILOT_HUMAN_AGGREGATE.json"
    human = json.loads(human_path.read_text()) if human_path.exists() else None
    report = summarize(rows, sources, private / "review_approval.json", human)
    (ROOT / "results/PILOT_SCREENING.json").write_text(json.dumps(report, indent=2) + "\n")
    counts = report["counts"]
    lines = [
        "# Pilot validation status", "",
        f"Screened sources: {counts['screened']} of {report['total_sources']}.",
        f"Eligible: {counts['eligible']}; ineligible: {counts['ineligible']}; "
        f"pending: {counts['pending']}; invalid: {counts['invalid']}.",
        f"Author-constructed edits: {counts['constructed_edits']}; "
        f"rejected: {counts['rejected_edits']}; impossible: {counts['impossible_edits']}.",
        f"Independent review plan approved: {'yes' if report['independent_review_plan_approved'] else 'no'}.",
        f"Independent human evidence: {report['independent_human_evidence']}.", "",
    ]
    if human:
        for rubric, value in human["rubrics"].items():
            lines.append(f"{rubric} observed relations: " + json.dumps(value["intended_to_observed"], sort_keys=True))
        lines.append("Compare validation yield and change directions with the pilot packet's planning targets. "
                     "The sample is mixed, and a human review of uncertainty and practical feasibility remains necessary.")
    else:
        lines.append("Go/no-go: pending. The predefined criteria require independent ratings, adjudication, "
                     "validated pairs in both relations and directions, and a precision review.")
    (ROOT / "results/PILOT_VALIDATION.md").write_text("\n".join(lines) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

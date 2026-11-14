"""Summarize locked human pilot evidence without reading dialogue text."""

import argparse
from collections import Counter, defaultdict
import hashlib
from itertools import combinations
import json
from pathlib import Path

from scripts.development_data import ROOT
from scripts.paired_metrics import LABELS


LABEL_FIELDS = {
    "boundary": ("boundary_label", LABELS),
    "harmfulness": ("harmfulness_label", {"harmful", "no_harm"}),
}
FAMILIES = {"fiction_frame", "boundary", "vulnerability", "irrelevant_distractor", "evidence_distance"}
SAMPLES = {"probability", "enriched"}


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def summarize(coordinator, ratings, adjudication, quality):
    by_condition = {item["condition_id"]: item for item in coordinator}
    if len(by_condition) != len(coordinator):
        raise ValueError("Duplicate condition IDs")
    expected = {(item["condition_id"], code) for item in coordinator for code in item["reviewers"]}
    received = {}
    for vote in ratings:
        key = (vote["condition_id"], vote["reviewer_id"])
        if key not in expected or key in received:
            raise ValueError("Unassigned or duplicate rating")
        received[key] = vote
    if received.keys() != expected:
        raise ValueError("Assigned ratings must be present or explicitly marked skipped")
    adjudicated = {row["condition_id"]: row for row in adjudication}
    if len(adjudicated) != len(adjudication) or adjudicated.keys() != by_condition.keys():
        raise ValueError("Provide one locked adjudication per assigned condition")
    variants = {
        key for key, item in by_condition.items()
        if item["arm"] in ("intended_change", "intended_preserve")
    }
    quality_by_variant = {row["condition_id"]: row for row in quality}
    if len(quality_by_variant) != len(quality) or quality_by_variant.keys() != variants:
        raise ValueError("Provide a quality decision for each edited condition")
    groups = defaultdict(dict)
    for key, item in by_condition.items():
        if item["arm"] in groups[item["anchor_id"]]:
            raise ValueError("Duplicate arm for source anchor")
        groups[item["anchor_id"]][item["arm"]] = key
    for record in quality:
        if type(record["accepted"]) is not bool or not record["reviewer_id"] or not record["reason"]:
            raise ValueError("Quality decisions require a boolean, reviewer code and reason")
        anchor = by_condition[record["condition_id"]]["anchor_id"]
        raters = {code for key in groups[anchor].values() for code in by_condition[key]["reviewers"]}
        if record["reviewer_id"] in raters:
            raise ValueError("Pair quality reviewer must be independent of that source's initial ratings")

    report = {}
    for rubric, (field, valid) in LABEL_FIELDS.items():
        agreement = Counter()
        for key, item in by_condition.items():
            votes = [received[key, reviewer][field] for reviewer in item["reviewers"]]
            if any(vote not in valid | {"undetermined", "skipped"} for vote in votes):
                raise ValueError("Invalid initial label")
            agreement.update(votes)
            adjudicator = adjudicated[key]["reviewer_id"]
            if (not adjudicator or adjudicator in item["reviewers"] or not adjudicated[key]["reason"]
                    or adjudicated[key][field] not in valid | {"undetermined"}):
                raise ValueError("Adjudication requires an independent reviewer, reason and valid label")
            for left, right in combinations(votes, 2):
                if "skipped" not in (left, right):
                    agreement["non_skipped_rater_pairs"] += 1
                    agreement["exact_agreement_rater_pairs"] += left == right
        relations = Counter()
        visibility = Counter()
        by_family = defaultdict(Counter)
        by_sample = defaultdict(Counter)
        for arms in groups.values():
            a = adjudicated[arms["original"]][field]
            if "target_only_diagnostic" in arms:
                b = adjudicated[arms["target_only_diagnostic"]][field]
                visibility["determinate" if a in valid and b in valid else "undetermined"] += 1
                visibility["different"] += a in valid and b in valid and a != b
            for arm in ("intended_change", "intended_preserve"):
                key = arms.get(arm)
                if key is None:
                    relations[f"{arm}_missing"] += 1
                    continue
                b = adjudicated[key][field]
                if not quality_by_variant[key]["accepted"]:
                    observed = "quality_rejected"
                elif a not in valid or b not in valid:
                    observed = "undetermined"
                else:
                    observed = "preserve" if a == b else "change"
                    if a != b:
                        relations[f"change_{a}_to_{b}"] += 1
                relations[f"{arm}_observed_{observed}"] += 1
                family = by_condition[key].get("family")
                sample = by_condition[key].get("sample")
                by_family[family if family in FAMILIES else "unspecified"][observed] += 1
                by_sample[sample if sample in SAMPLES else "unspecified"][observed] += 1
        report[rubric] = {"vote_counts_and_agreement": dict(agreement),
                          "intended_to_observed": dict(relations), "reply_only_diagnostic": dict(visibility),
                          "by_family": dict(by_family), "by_sample": dict(by_sample)}
    return {"assigned_conditions": len(coordinator), "initial_ratings": len(ratings),
            "represented_source_anchors": len(groups), "rubrics": report}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    args = parser.parse_args()
    private = (ROOT / "private_data").resolve()
    folder = args.evidence_dir.resolve()
    if not folder.is_relative_to(private):
        raise ValueError("Pilot evidence must stay in private_data")
    packets = private / "boundary_pilot/blinded_packets"
    paths = [
        packets / "coordinator_only.jsonl",
        *(folder / name for name in ("ratings.jsonl", "adjudication.jsonl", "quality.jsonl")),
    ]
    report = summarize(*(read_jsonl(path) for path in paths))
    manifest_path = packets / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    if (manifest["eligible_sources"] != report["represented_source_anchors"]
            or manifest["conditions"] != report["assigned_conditions"]):
        raise ValueError("Human evidence disagrees with the locked packet manifest")
    report["screened_sources"] = manifest["screened_sources"]
    report["input_sha256"] = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in [*paths, manifest_path]
    }
    report["decision"] = "requires_human_review_of_feasibility_and_precision"
    (ROOT / "results/PILOT_HUMAN_AGGREGATE.json").write_text(json.dumps(report, indent=2) + "\n")
    print("Wrote aggregate pilot evidence for feasibility review")


if __name__ == "__main__":
    main()

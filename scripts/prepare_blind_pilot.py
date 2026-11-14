"""Validate locally drafted pilot arms and make blinded reviewer packets."""

import argparse
from collections import defaultdict
import hashlib
import json
import os
from pathlib import Path
import random
import re
import secrets

from scripts.audit_conversation_overlap import parse_prefix
from scripts.development_data import ROOT, load_development


ARMS = ("original", "intended_change", "intended_preserve")
FAMILIES = {"fiction_frame", "boundary", "vulnerability", "irrelevant_distractor", "evidence_distance"}


def valid_structure(original, edited, family):
    old_roles = tuple(role for role, _ in original)
    new_roles = tuple(role for role, _ in edited)
    replacement = old_roles == new_roles and sum(a != b for a, b in zip(original, edited)) == 1
    if family == "irrelevant_distractor":
        insertion = len(edited) == len(original) + 1 and any(
            edited[:i] + edited[i + 1:] == original for i in range(len(edited))
        )
        return replacement or insertion
    if family == "evidence_distance":
        if len(original) != len(edited):
            return False
        return any(
            original[i] == edited[j] and original[:i] + original[i + 1:] == edited[:j] + edited[j + 1:]
            for i in range(len(original)) for j in range(len(edited)) if i != j
        )
    return replacement


def candidate_arms(entry, source):
    if (entry["target"] != source.target or entry["original_prefix"] != source.raw_context
            or entry["source_conversation_id"] != source.conversation
            or hashlib.sha256(source.target.encode()).hexdigest() != entry["target_sha256"]):
        raise ValueError("Pilot entry does not match its pinned source")
    screening = entry["screening_status"]
    if screening == "ineligible" and entry["screening_reason"]:
        return {}
    if screening != "eligible":
        raise ValueError("Each queued source needs a completed screening decision")
    arms = {"original": source.prefix}
    for arm in ARMS[1:]:
        edit = entry["edits"][arm]
        if edit["status"] in ("not_constructible", "rejected") and edit.get("reason"):
            continue
        if edit["status"] != "constructed" or edit["family"] not in FAMILIES or not edit["prefix"]:
            raise ValueError("Each slot needs a constructed edit or a reason it could not be made")
        if edit.get("decision") not in ("accept", "modify"):
            raise ValueError("A constructed edit requires the human author's accept or modify decision")
        if edit["decision"] == "accept":
            key = "change" if arm == "intended_change" else "preserve"
            suggestions = [
                run.get("edits", {}).get(key)
                for run in entry.get("model_suggestions", {}).values()
            ]
            if not any(
                suggestion and suggestion.get("prefix") == edit["prefix"]
                and suggestion.get("family") == edit["family"]
                for suggestion in suggestions
            ):
                raise ValueError("Accepted edit must match a displayed model suggestion")
        prefix = parse_prefix(edit["prefix"])
        if prefix is None or not valid_structure(source.prefix, prefix, edit["family"]):
            raise ValueError("An edit does not meet its intervention family's structural rule")
        if prefix in arms.values():
            raise ValueError("An edited prefix duplicates an existing arm")
        arms[arm] = prefix
    return arms


def assign(groups, reviewers, seed=42, condition_id=lambda: secrets.token_hex(12)):
    required = 3 * max(len(arms) for _, _, arms in groups)
    if len(set(reviewers)) != len(reviewers) or len(reviewers) < required:
        raise ValueError(f"Use at least {required} distinct reviewer codes for three ratings per arm")
    rng = random.Random(seed)
    records = defaultdict(list)
    coordinator = []
    seen_ids = set()
    seen_groups = set()
    for entry, target, arms in groups:
        source = entry["source_conversation_id"]
        if source in seen_groups:
            raise ValueError("The pilot requires one source reply per conversation")
        seen_groups.add(source)
        arm_names = list(arms)
        rng.shuffle(arm_names)
        roster = list(reviewers)
        rng.shuffle(roster)
        roster.sort(key=lambda code: len(records[code]))
        for i, arm in enumerate(arm_names):
            key = condition_id()
            if key in seen_ids:
                raise ValueError("Duplicate condition ID")
            seen_ids.add(key)
            codes = roster[3 * i:3 * i + 3]
            coordinator.append({"condition_id": key, "anchor_id": entry["anchor_id"],
                                "source_conversation_id": source, "arm": arm,
                                "family": entry.get("edits", {}).get(arm, {}).get("family"),
                                "sample": entry.get("sample"),
                                "target_sha256": entry["target_sha256"], "reviewers": codes})
            visible = {
                "condition_id": key,
                "turns": [{"turn": n, "speaker": role, "text": body}
                          for n, (role, body) in enumerate(arms[arm], 1)],
                "target": target,
            }
            for code in codes:
                records[code].append(visible)
    for items in records.values():
        rng.shuffle(items)
    return records, coordinator


def write_jsonl(path, rows):
    with path.open("x", encoding="utf-8") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")


def check_approval(path, reference):
    if not path.is_file():
        raise ValueError("Independent-review plan approval has not been recorded")
    approval = json.loads(path.read_text())
    if (approval.get("status") != "approved" or approval.get("reference") != reference
            or not approval.get("approved_by") or not approval.get("approved_on")):
        raise ValueError("Independent-review approval record is incomplete or does not match")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--drafts", type=Path, required=True)
    parser.add_argument("--reviewers", nargs="+", required=True)
    parser.add_argument("--target-only-count", type=int, default=10)
    parser.add_argument("--authorization-ref", required=True, help="Reference to the approved G2 review plan.")
    args = parser.parse_args()
    if not args.authorization_ref.strip() or any(
        not re.fullmatch(r"[a-zA-Z0-9_-]{1,30}", code) for code in args.reviewers
    ):
        raise ValueError("Provide an authorization reference and safe reviewer codes")
    private = (ROOT / "private_data").resolve()
    check_approval(private / "boundary_pilot/review_approval.json", args.authorization_ref)
    if not args.drafts.resolve().is_relative_to(private):
        raise ValueError("Keep the drafts in private_data")
    datasets, provenance = load_development()
    sources = {row.utterance: row for row in datasets["dev"]}
    entries = [json.loads(line) for line in args.drafts.read_text().splitlines() if line.strip()]
    if len(entries) != 50 or len({entry["anchor_id"] for entry in entries}) != 50:
        raise ValueError("Supply the 50 uniquely identified pilot screening records")
    queue = private / "boundary_pilot/authoring_queue.jsonl"
    selected = {item["anchor_id"]: item["source_utterance_id"]
                for item in map(json.loads, queue.read_text().splitlines())}
    if {item["anchor_id"]: item["source_utterance_id"] for item in entries} != selected:
        raise ValueError("Drafts differ from the selected pilot sources")
    groups = []
    for entry in entries:
        source = sources[entry["source_utterance_id"]]
        arms = candidate_arms(entry, source)
        if arms:
            groups.append((entry, source.target, arms))
    if not groups:
        raise ValueError("The pilot has no eligible arms")
    if args.target_only_count < 0:
        raise ValueError("Target-only count cannot be negative")
    target_only = random.Random(42).sample(groups, min(args.target_only_count, len(groups)))
    for _, _, arms in target_only:
        arms["target_only_diagnostic"] = ()
    packets, coordinator = assign(groups, args.reviewers)
    os.umask(0o077)
    out = private / "boundary_pilot" / "blinded_packets"
    out.mkdir(mode=0o700)
    for reviewer, packet in packets.items():
        write_jsonl(out / f"reviewer_{reviewer}.jsonl", packet)
    write_jsonl(out / "coordinator_only.jsonl", coordinator)
    (out / "manifest.json").write_text(json.dumps({
        "authorization_ref": args.authorization_ref, "provenance": provenance,
        "screened_sources": len(entries), "eligible_sources": len(groups), "conditions": len(coordinator),
        "target_only_diagnostic_conditions": len(target_only),
    }, indent=2) + "\n")
    print(f"Prepared {len(coordinator)} blinded conditions for authorized local review")


if __name__ == "__main__":
    main()

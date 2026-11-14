"""Create a private development-only queue for pilot editing and screening."""

from collections import Counter, defaultdict
import csv
import hashlib
import hmac
import json
import os
import random

from scripts.development_data import ROOT, load_development


SEED = 42
RANDOM_SOURCES = 25
ENRICHED_SOURCES = 25


def select(rows, disagreements):
    groups = defaultdict(list)
    for row in rows:
        if len(row.prefix) >= 2 and any(role == "User" for role, _ in row.prefix):
            groups[row.conversation].append(row)
    if len(groups) < RANDOM_SOURCES + ENRICHED_SOURCES:
        raise ValueError("Insufficient context-eligible source conversations")
    rng = random.Random(SEED)
    population = sorted(groups)
    random_groups = set(rng.sample(population, RANDOM_SOURCES))
    random_items = [
        (rng.choice(groups[key]), "probability", RANDOM_SOURCES / len(groups) / len(groups[key]))
        for key in sorted(random_groups)
    ]

    # Enrich the separate stress sample for classifier and annotator disagreement.
    strata = defaultdict(list)
    for key in population:
        if key in random_groups:
            continue
        candidates = groups[key][:]
        rng.shuffle(candidates)
        row = min(candidates, key=lambda item: (item.utterance not in disagreements, -len(item.prefix)))
        strata[row.label, row.votes, row.category, len(row.prefix) >= 5].append(row)
    for bucket in strata.values():
        rng.shuffle(bucket)
        bucket.sort(key=lambda item: item.utterance in disagreements)
    order = sorted(strata)
    rng.shuffle(order)
    enriched = []
    while len(enriched) < ENRICHED_SOURCES:
        for key in order:
            if strata[key]:
                enriched.append((strata[key].pop(), "enriched", None))
                if len(enriched) == ENRICHED_SOURCES:
                    break
    return random_items + enriched, len(groups)


def read_disagreements(audit):
    out = ROOT / "private_data" / audit["run_id"]
    key = (out / "pseudonym_key").read_bytes()
    path = out / "predictions.csv"
    if hashlib.sha256(path.read_bytes()).hexdigest() != audit["prediction_sha256"]:
        raise ValueError("Development predictions changed since audit")
    by_item = defaultdict(dict)
    with path.open(newline="") as stream:
        for row in csv.DictReader(stream):
            if row["condition"] in ("target_model", "full"):
                by_item[row["reply_id"]][row["condition"]] = row["prediction"]
    pseudonyms = {item for item, values in by_item.items() if values["target_model"] != values["full"]}
    return key, pseudonyms


def main():
    data, provenance = load_development()
    audit = json.loads((ROOT / "results/CONTEXT_AUDIT_DEV.json").read_text())
    if audit["provenance"] != provenance:
        raise ValueError("Pilot source differs from the development audit")
    key, pseudonyms = read_disagreements(audit)
    disagreements = {
        row.utterance for row in data["dev"]
        if hmac.digest(key, f"reply:{row.utterance}".encode(), "sha256").hex() in pseudonyms
    }
    cases, population = select(data["dev"], disagreements)
    out = ROOT / "private_data" / "boundary_pilot"
    os.umask(0o077)
    out.mkdir(mode=0o700, exist_ok=True)
    with (out / "authoring_queue.jsonl").open("x", encoding="utf-8") as stream:
        for i, (row, sample, inclusion) in enumerate(cases, 1):
            record = {
                "anchor_id": f"P{i:03d}", "source_conversation_id": row.conversation,
                "source_utterance_id": row.utterance, "sample": sample,
                "random_sample_inclusion_probability": inclusion,
                "upstream_category": row.category, "upstream_majority_votes": row.votes,
                "development_models_disagree": row.utterance in disagreements,
                "original_prefix": row.raw_context, "target": row.target,
                "target_sha256": hashlib.sha256(row.target.encode()).hexdigest(),
                "screening_status": "pending", "screening_reason": None,
                "edits": {
                    "intended_change": {"prefix": None, "family": None, "status": "pending"},
                    "intended_preserve": {"prefix": None, "family": None, "status": "pending"},
                },
            }
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")
    summary = {
        "source_split": "dev", "seed": SEED, "source_selection_frame_conversations": population,
        "selected_by_sample": dict(Counter(sample for _, sample, _ in cases)),
        "unique_source_conversations": len({row.conversation for row, _, _ in cases}),
        "edit_slots": 2 * len(cases), "constructed_edits": 0, "human_ratings": 0,
        "eligibility": "at least two preceding turns, at least one user turn; manual boundary screening pending",
        "provenance": provenance, "development_audit_run_id": audit["run_id"],
        "queue_sha256": hashlib.sha256((out / "authoring_queue.jsonl").read_bytes()).hexdigest(),
    }
    (ROOT / "results/PILOT_QUEUE.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(f"Prepared {len(cases)} local source records for authoring")


if __name__ == "__main__":
    main()

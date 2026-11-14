"""Prepare an editable local pilot draft file with model suggestions attached."""

import hashlib
import json
import os

from scripts.development_data import ROOT
from scripts.prepare_blind_pilot import write_jsonl


def main():
    os.umask(0o077)
    folder = ROOT / "private_data/boundary_pilot"
    queue = folder / "authoring_queue.jsonl"
    cases = list(map(json.loads, queue.read_text().splitlines()))
    queue_hash = hashlib.sha256(queue.read_bytes()).hexdigest()
    runs = {}
    for label, suffix in (("boundary", ""), ("broad", "_broad")):
        config = json.loads((folder / f"model_draft_config{suffix}.json").read_text())
        if config["queue_sha256"] != queue_hash:
            raise ValueError("Draft run used a different source queue")
        records = list(map(json.loads, (folder / f"model_drafts{suffix}.jsonl").read_text().splitlines()))
        runs[label] = {record["anchor_id"]: record for record in records}
        if len(records) != len(cases) or runs[label].keys() != {case["anchor_id"] for case in cases}:
            raise ValueError("Wait until all pilot sources have drafting records")
    for case in cases:
        case["model_suggestions"] = {label: records[case["anchor_id"]]
                                     for label, records in runs.items()}
    write_jsonl(folder / "review_drafts.jsonl", cases)
    print(f"Attached two local drafting passes to {len(cases)} editable screening records")


if __name__ == "__main__":
    main()

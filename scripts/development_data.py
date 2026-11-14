"""Load verified CompanionHarm development inputs from local storage."""

import csv
from dataclasses import dataclass
import hashlib
import io
import json
from pathlib import Path

from scripts.audit_companionharm import MANIFEST, binary_label, read_pinned_split
from scripts.audit_conversation_overlap import parse_prefix


ROOT = Path(__file__).resolve().parents[1]
DEV_SPLITS = ("train", "dev")


@dataclass(frozen=True)
class Reply:
    utterance: str
    conversation: str
    prefix: tuple
    raw_context: str
    target: str
    label: int
    category: str
    votes: int


def load_development():
    manifest = json.loads(MANIFEST.read_text())
    source = next(item for item in manifest["sources"] if item["id"] == "companionharm")
    folder = ROOT / "private_data/companionharm" / source["revision"] / "data/splits"
    exclusions_bytes = (folder / "proposed_conversation_exclusions.json").read_bytes()
    exclusions = json.loads(exclusions_bytes)
    if exclusions["source_revision"] != source["revision"]:
        raise ValueError("Exclusions do not match the pinned source")
    expected = {Path(item["path"]).stem: item for item in source["data_objects"]}
    datasets = {}
    for split in DEV_SPLITS:
        payload = read_pinned_split(folder / f"{split}.csv", expected[split])
        if hashlib.sha256(payload).hexdigest() != expected[split]["raw_bytes_sha256"]:
            raise ValueError("Pinned source hash differs")
        excluded = set(exclusions["exclude_conversation_ids"][split])
        with io.TextIOWrapper(io.BytesIO(payload), encoding="utf-8-sig", newline="") as stream:
            rows = []
            for row in csv.DictReader(stream):
                if row["conversation_id"] in excluded:
                    continue
                prefix = parse_prefix(row["context"])
                label = binary_label(row["label"])
                if prefix is None or len(prefix) != int(row["line_number"]) - 1 or label is None:
                    raise ValueError("Invalid audited source row")
                rows.append(Reply(
                    row["utterance_id"], row["conversation_id"], prefix, row["context"],
                    row["current_line"], int(label == "harmful"), row["label"],
                    int(row["majority_vote_count"]),
                ))
        datasets[split] = rows
    provenance = {
        "source_revision": source["revision"],
        "split_sha256": {split: expected[split]["raw_bytes_sha256"] for split in DEV_SPLITS},
        "exclusions_sha256": hashlib.sha256(exclusions_bytes).hexdigest(),
    }
    return datasets, provenance

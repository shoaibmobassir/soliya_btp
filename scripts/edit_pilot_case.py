"""Edit one local pilot case using the user's terminal editor."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import tempfile

from scripts.development_data import ROOT, load_development
from scripts.prepare_blind_pilot import candidate_arms


def read_queue(path):
    content = path.read_bytes()
    rows = [json.loads(line) for line in content.decode("utf-8").splitlines() if line.strip()]
    if len(rows) != 50 or len({row["anchor_id"] for row in rows}) != 50:
        raise ValueError("The private queue must contain 50 distinct source records")
    return content, rows


def validate_revision(original, edited, sources):
    immutable = ("anchor_id", "source_conversation_id", "source_utterance_id",
                 "original_prefix", "target", "target_sha256", "sample",
                 "random_sample_inclusion_probability", "upstream_category",
                 "upstream_majority_votes", "development_models_disagree", "model_suggestions")
    if any(original.get(key) != edited.get(key) for key in immutable):
        raise ValueError("Source identity and model suggestions must remain unchanged")
    source = sources.get(original["source_utterance_id"])
    if source is None:
        raise ValueError("Source is absent from the verified development cohort")
    if edited["screening_status"] == "pending":
        return
    candidate_arms(edited, source)


def author_view(entry, rows):
    matches = [row for row in rows if row.conversation == entry["source_conversation_id"]]
    if not matches:
        raise ValueError("Source conversation not found in development data")
    sequences = [
        (*row.prefix, ("Replika", row.target.partition(":")[2].strip()))
        for row in matches
    ]
    longest = max(sequences, key=len)
    if any(longest[:len(sequence)] != sequence for sequence in sequences):
        raise ValueError("Inconsistent source conversation prefixes")
    return {
        "coverage": "Longest conversation trace available in the released development split. "
                    "Later turns may be unavailable. Independent raters receive the focal prefix only.",
        "turns": [{"turn": i, "speaker": role, "text": text}
                  for i, (role, text) in enumerate(longest, 1)],
        "focal_reply": entry["target"],
        "original_annotation_category": entry["upstream_category"],
        "candidate_suggestions": entry.get("model_suggestions", {}),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", required=True, help="Opaque pilot ID, for example P001")
    args = parser.parse_args()
    path = ROOT / "private_data/boundary_pilot/review_drafts.jsonl"
    before, rows = read_queue(path)
    positions = [i for i, row in enumerate(rows) if row["anchor_id"] == args.case]
    if len(positions) != 1:
        raise ValueError("Pilot case ID not found")
    index = positions[0]
    datasets, _ = load_development()
    sources = {row.utterance: row for row in datasets["dev"]}
    editor = shlex.split(os.environ.get("VISUAL") or os.environ.get("EDITOR") or "nano")
    if not editor:
        raise ValueError("Set VISUAL or EDITOR to a terminal editor")
    os.umask(0o077)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         suffix=".json", delete=False) as stream:
            temporary = Path(stream.name)
            view = {"source_view": author_view(rows[index], datasets["dev"]), "decision": rows[index]}
            json.dump(view, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        subprocess.run([*editor, str(temporary)], check=True)
        view = json.loads(temporary.read_text(encoding="utf-8"))
        if view["source_view"] != author_view(rows[index], datasets["dev"]):
            raise ValueError("The source view is read-only")
        edited = view["decision"]
        validate_revision(rows[index], edited, sources)
        if hashlib.sha256(path.read_bytes()).digest() != hashlib.sha256(before).digest():
            raise ValueError("The queue changed while this case was open; no changes were saved")
        rows[index] = edited
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         delete=False) as stream:
            replacement = Path(stream.name)
            for row in rows:
                stream.write(json.dumps(row, ensure_ascii=False) + "\n")
        replacement.replace(path)
        print(f"Saved {args.case} locally with screening status {edited['screening_status']}.")
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    main()

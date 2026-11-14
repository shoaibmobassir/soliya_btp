"""Report role-aware prefix integrity and cross-split text overlap as counts."""

import argparse
from collections import Counter, defaultdict
import csv
import io
from itertools import combinations
import json
from pathlib import Path
import re
import sys
import tempfile

from scripts.audit_companionharm import (
    MANIFEST, SPLITS, AuditError, audit_splits, normalize_text, read_pinned_split,
)


ROLE = re.compile(r"(?m)^(User|Replika):[ \t]*")
MIN_SHINGLES = 5
JACCARD_NUMERATOR = 4
JACCARD_DENOMINATOR = 5


def parse_prefix(text):
    if not text.strip():
        return ()
    markers = list(ROLE.finditer(text))
    if not markers or text[:markers[0].start()].strip():
        return None
    ends = [marker.start() for marker in markers[1:]] + [len(text)]
    return tuple(
        (marker.group(1), normalize_text(text[marker.end():end]))
        for marker, end in zip(markers, ends)
    )


def reconstruct_split(payload):
    counts = Counter({
        "invalid_prefix_rows": 0,
        "invalid_target_role_rows": 0,
        "prefix_length_mismatches": 0,
        "prefix_consistency_mismatches": 0,
        "exact_target_at_earlier_ai_turn": 0,
        "exact_target_at_earlier_user_turn": 0,
    })
    observations = defaultdict(list)
    with io.TextIOWrapper(io.BytesIO(payload), encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            prefix = parse_prefix(row["context"])
            if prefix is None:
                counts["invalid_prefix_rows"] += 1
                continue
            line_number = int(row["line_number"])
            if len(prefix) != line_number - 1:
                counts["prefix_length_mismatches"] += 1
                continue
            target_role, separator, target_body = row["current_line"].partition(":")
            if separator != ":" or target_role != "Replika":
                counts["invalid_target_role_rows"] += 1
                continue
            target = normalize_text(target_body)
            counts["exact_target_at_earlier_ai_turn"] += ("Replika", target) in prefix
            counts["exact_target_at_earlier_user_turn"] += ("User", target) in prefix
            observations[row["conversation_id"]].append(prefix + (("Replika", target),))
    traces = {}
    for conversation, seen_prefixes in observations.items():
        longest = max(seen_prefixes, key=len)
        if any(longest[:len(prefix)] != prefix for prefix in seen_prefixes):
            counts["prefix_consistency_mismatches"] += 1
        traces[conversation] = longest
    counts["reconstructed_conversations"] = len(traces)
    return dict(counts), traces


def shingles(trace):
    words = []
    for role, body in trace:
        words.append(f"<{role}>")
        words.extend(re.findall(r"\w+", body.casefold()))
    return set(zip(words, words[1:], words[2:]))


def match_traces(left, right):
    matches = {"exact": set(), "near": set()}
    right_exact = defaultdict(set)
    right_index = defaultdict(set)
    right_shingles = {key: shingles(trace) for key, trace in right.items()}
    for key, trace in right.items():
        right_exact[trace].add(key)
        tokens = right_shingles[key]
        if len(tokens) >= MIN_SHINGLES:
            for token in tokens:
                right_index[token].add(key)
    for left_key, trace in left.items():
        exact = right_exact[trace]
        matches["exact"].update((left_key, right_key) for right_key in exact)
        tokens = shingles(trace)
        if len(tokens) < MIN_SHINGLES:
            continue
        candidates = set().union(*(right_index[token] for token in tokens if token in right_index))
        for right_key in candidates - exact:
            other = right_shingles[right_key]
            intersection = len(tokens & other)
            union = len(tokens) + len(other) - intersection
            if intersection * JACCARD_DENOMINATOR >= union * JACCARD_NUMERATOR:
                matches["near"].add((left_key, right_key))
    return matches


def context_reply_index(payload):
    index = defaultdict(set)
    with io.TextIOWrapper(io.BytesIO(payload), encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            context = normalize_text(row["context"])
            target = normalize_text(row["current_line"])
            if context and target:
                index[context, target].add(row["conversation_id"])
    return index


def write_private_exclusions(folder, revision, exclusions):
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=folder, delete=False
    ) as stream:
        temporary_path = Path(stream.name)
        json.dump({
            "source_revision": revision,
            "exclude_conversation_ids": {split: sorted(ids) for split, ids in exclusions.items()},
        }, stream, indent=2)
        stream.write("\n")
    temporary_path.replace(folder / "proposed_conversation_exclusions.json")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split-dir", type=Path, required=True)
    parser.add_argument("--write-private-exclusions", action="store_true",
                        help="Write proposed exclusion IDs beside the splits in an owner-only directory.")
    args = parser.parse_args()
    try:
        manifest = json.loads(MANIFEST.read_text())
        source = next(entry for entry in manifest["sources"] if entry["id"] == "companionharm")
        audit = audit_splits(args.split_dir, source)
        if audit["blocking_integrity_findings"]:
            raise AuditError("base_integrity_checks_failed")
        by_path = {item["path"]: item for item in source["data_objects"]}
        summaries, traces, row_indexes = {}, {}, {}
        for split in SPLITS:
            expected = by_path[f"data/splits/{split}.csv"]
            payload = read_pinned_split(args.split_dir / f"{split}.csv", expected)
            summaries[split], traces[split] = reconstruct_split(payload)
            row_indexes[split] = context_reply_index(payload)
        overlaps = {}
        exclusions = {split: set() for split in SPLITS}
        for left, right in combinations(SPLITS, 2):
            matches = match_traces(traces[left], traces[right])
            overlaps[f"{left}-{right}"] = {
                f"{kind}_trace_pairs": len(pairs) for kind, pairs in matches.items()
            }
            for left_key, right_key in matches["exact"] | matches["near"]:
                exclusions[left].add(left_key)
                exclusions[right].add(right_key)
            left_rows, right_rows = row_indexes[left], row_indexes[right]
            for shared in left_rows.keys() & right_rows.keys():
                exclusions[left].update(left_rows[shared])
                exclusions[right].update(right_rows[shared])
        if args.write_private_exclusions:
            if args.split_dir.stat().st_mode & 0o077:
                raise AuditError("exclusion_directory_must_be_owner_only")
            write_private_exclusions(args.split_dir, source["revision"], exclusions)
    except (AuditError, OSError, UnicodeError, csv.Error, ValueError, KeyError, StopIteration):
        print("Conversation overlap audit failed. Verify the pinned inputs locally.", file=sys.stderr)
        return 2
    print(json.dumps({
        "source_revision": source["revision"],
        "integrity": audit,
        "prefix_checks": summaries,
        "cross_split_trace_pairs": overlaps,
        "proposed_excluded_conversations": {split: len(ids) for split, ids in exclusions.items()},
        "minimum_shingles": MIN_SHINGLES,
        "jaccard_threshold": JACCARD_NUMERATOR / JACCARD_DENOMINATOR,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())

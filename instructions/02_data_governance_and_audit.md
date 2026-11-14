# Stage 0B — data audit and rights

**Deliverables:** `results/DATA_AUDIT.md`, `results/LICENSE_LEDGER.md`, `results/OVERLAP_AUDIT.md`, `data/source_manifest.json`, tests.

1. Read the upstream CompanionHarm README/LICENSE/data card and source CSV headers. Verify 4222/1403/1391 row counts, 1268/423/420 conversations, no conversation overlap. Do not assume pasted summaries are current file reality.
2. Parse original 14-class labels, per-item vote/agreement, role/turn structure and target/context fields. Preserve originals untouched. Derive binary `no harmful behavior -> safe`, other valid harm labels -> harmful. Document any ambiguous/no-majority records separately.
3. Compute counts of empty context by source/turn, exact target-context match and substring overlap, duplicate IDs, full-row duplicates. Do not assume substring overlap = leakage.
4. Assess conversation-level and near-duplicate cross-corpus overlap using normalized text, n-gram MinHash/LSH or similar. Manually review flagged *metadata-safe* matches under approved access. Never post raw strings in logs.
5. Verify AICompanionBench data license, schema, label unit, categories, pre-filter selection and label-generation process; do not treat 2123 conversation-level labels as utterance-level. If rights unclear, do not download/redistribute its raw text; log blocker and request permission.
6. Record provenance checksums, access date, license terms, code/data separate rights, allowed local processing, API transfer rules, release permissions, source and contact restrictions.
7. Add tests: source not modified; no split leakage; target-preservation hash; no raw content in exported logs; deterministic derived labels.

# Mandatory stage gates and kill criteria

| Gate | Required evidence | Go/no-go |
|---|---|---|
| G0 Prior art + rights | 15+ directly relevant peer-reviewed/preprint sources with full-text methodological comparisons where possible; dataset terms ledger | Stop if near-identical paper already makes claimed contribution or rights forbid use |
| G1 Provenance + split integrity | dataset manifest, checksums, exact/fuzzy overlap checks, input leak audit, originals unmodified | Stop if provenance/splits untrusted until fixed |
| G2 Ethics + annotation | approved data-access and annotator safety plan; informed instructions; secure review platform | No human data handling beyond approved boundary |
| G3 Pilot | blind double/triple annotations for ~50 originals +100 edits; validation rates by family, uncertainty; pilot report | Reject/redo weak or nonsensical interventions; no arbitrary post hoc passing threshold |
| G4 Protocol freeze | locked hypotheses/metrics/primary contrasts/holdout definition, timestamped hash | No confirmatory test access before lock |
| G5 Baseline replication | baseline scripts and tests; results compared with original reported metrics and discrepancies logged | No experimental comparison with broken baseline |
| G6 Benchmark validity | completed independent human validation; attrition, label balance, disjoint groups | Stop if label-flip/preserving gold cannot be reliably established |
| G7 Analysis | raw-safe prediction records, CIs, seeded reproducible tables, held-out test once | No publishing claims without analysis audit |
| G8 Conditional method/external | comparable baselines, cost accounting, crosswalk and provenance audit | Can omit; never pretend completed |
| G9 Paper readiness | reproducibility report, citation checks, limitations and ethics, reviewer reports | Manuscript must label results TBD until actually measured |

**Kill criteria:** direct prior-art duplicate; unverifiable data license; privacy constraints that prevent ethical annotations; insufficient valid counterfactuals; unfixable provenance contamination. If reached, write a stop/pivot memo rather than forcing a paper.

# Stage 3 — full ContextEvidenceBench

Prerequisites G3 + G4. Target size is 300 anchors + 600 edits + independent ratings; amend after pilot precision calculation.

- Build balanced, pre-specified sampling across relationship-specific harms, other harms, safe near-misses, model disagreement and an unconditioned probability sample. Clearly distinguish benchmark mixture from real prevalence.
- Use versioned transformation templates/scripts. Preserve exact target response, role coherence, linguistic fluency, relevant causal factor isolation, and context length controls when possible.
- Separate **intended** edit relation from **human-validated** gold relation; only adjudicated valid pairs enter confirmatory paired metrics; report attrition and ambiguous cases separately.
- Annotation quality: blinded pair assignment, 3 independent raters per condition target, independent adjudication; track `no consensus`, multi-label cases, annotator training, rubric changes. Where category-to-binary mapping masks meaningful ambiguity, analyze category-specific relations.
- Freeze benchmark subsets and minimize textual memorization across train/dev/test. Cluster all variants under source conversation; when templates are repeated, report template-holdout results. Training/routing agents cannot see evaluation pairs.
- Suggested benchmark versioning: semantic `v0.1-pilot`, `v1.0-locked`; generate `manifest.json`, checksum lists, field-level documentation and private/public release separation.
- Build a `benchmark_quality_report`: edit success, coherence, agreement, label relation, diversity, risk of synthetic artifacts, prevalence caveats.
- Do not release raw/derived dialogue unless upstream rights and ethics review permit it. Publish only allowed metadata, scripts and synthetic illustrative cases where necessary.

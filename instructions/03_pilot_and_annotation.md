# Stage 1 — 50-target falsification pilot and blinded annotation

**Do not run human annotation until G2 is passed.**

Pilot intended size (not completed): 50 originating utterances with enough actual preceding context; two edited variants each, 150 conditions total. Add candidate oversampling because invalid cases may be discarded.

1. Preregister selection stratification (harm/safe, class, context length, annotator agreement, disagreement between existing classifiers) and include a random sample. Group by conversation and ensure editing/analysis cohorts do not contaminate final test.
2. Hold exact AI target bytes identical across anchor/edits and prove with SHA256; all edits to preceding conversation only. Prevent breaking role/time coherence.
3. Produce exactly one intended label-preserving and one intended label-changing edit per anchor **only where plausible**; allow `not constructible`. Families: roleplay framing; consent/boundary; risk-relevant disclosure; irrelevant emotional distractor; ordering/distance. Edit operations must be minimally invasive; no contrived contradictions.
4. Human annotation UI/CSV: independently presented variants, blinded pair membership and intended label; randomized assignments and presentation order. At least 3 ratings per condition if available, with adjudication plan; ask binary judgment, optional original taxonomy class, supporting turns, confidence, coherence, and reviewer uncertainty. Avoid making reviewer choose 'changed' or 'unchanged' unless using an independent second-stage pair reviewer.
5. Analyze validation rate and rejected reasons per family, annotation disagreement, split-level provenance, and whether gold label relations agree with edit intents. Validate against synthetic known-answer fixtures first.
6. Use a pilot protocol decision document to adjust wording/criteria only **before** protocol lock and held-out test. Do not tune models on final test. Record all changes with timestamps.
7. Write `results/PILOT_REPORT.md` including a recommendation: expand / redesign / halt. No arbitrary post hoc thresholds; define practical thresholds prospectively based on pilot precision and annotation feasibility.

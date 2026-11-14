# Stage 0A — adversarial novelty validation

**Deliverables:** `results/PRIOR_ART_MATRIX.csv`, `results/NOVELTY_VERDICT.md`, `results/SOURCE_LEDGER.md`, and four role reports.

1. Search (with date recorded) arXiv, ACL Anthology, OpenReview, ACM, Semantic Scholar, Google Scholar, IEEE, GitHub. If tools unavailable mark unavailable, do not invent searches.
2. Must review these starting points, verify full text/appendices and date: CompanionHarm 2608.25377; AICompanionBench 2606.04867; CompanionSafe 2610.18095; ConCI 2610.24494; When Context Flips Safety Breaks 2605.27851; No Convo! 2026.findings-aacl.204; Pavlopoulos et al. ACL 2020; Context Sensitivity Estimation WOAH 2021; Nature Medicine clinical counterfactual chatbot audit DOI 10.1038/s41591-026-04577-2; CHIVE 2026; Persona-Grounded AI Companion safety ACL 2026.
3. Search specific claims, not only title: `fixed response different context safety label human validated`; `label-preserving and label-changing context intervention moderation`; `AI companion harmfulness contextual evidence perturbation`; `context sensitivity necessity sufficiency annotation`.
4. Compare for each source: target task, input unit, whether exact target held fixed, interventions, whether correct relation independently human-validated, label construction, evaluation metrics, companion-specificity, dataset/protocol release, and precise overlapping claim. Quote no long passages.
5. Classify `direct duplicate`, `substantial overlap`, `background`, or `unresolved`. Cite URL/DOI, date, and page/section when available; distinguish `checked full text` from `abstract-only`.
6. Independent validator must attempt to **reject** the central novelty claim. If exact task/protocol already exists, stop or narrow the contribution with evidence. No fake percentage confidence.
7. Produce a concise verdict: `GO_PILOT`, `REVISE`, or `STOP`, with falsifiable minimum novel contribution.

Do not claim originality for triplets, counterfactual edits, human validation, context-need prediction, ordinary context ablations, or cross-dataset transfer alone.

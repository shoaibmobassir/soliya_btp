# Stage 5 (OPTIONAL) — cost-aware selective context and human review

Skip unless G3/G6 support meaningful contextual errors and sufficient development data. This is NOT the core novelty.

- Actions: KEEP target-only, ACQUIRE_CONTEXT then classify, REVIEW by human. Define reviewer error as measured where possible, otherwise sensitivity scenarios; never assume perfection without labeling it an oracle bound.
- Context need target derived by **out-of-fold** predictions on training data only. No leakage from model training or benchmark evaluation. Compare uncertainty, disagreement, random, context-need predictor, learning-to-defer/feature-acquisition baseline.
- Cost model: C_total = N_target*C_target + N_context*C_context + N_review*C_review plus overhead. Unit-normalize measurement for inference latency, tokens and annotation minutes. Do not equate '20% touched' with equal budget across actions.
- Choose budgets and thresholds on development. Report risk vs actual total cost and separate harm miss rate, safe FPR, review workload. Include realistic reviewer errors and latency constraints. Test under shifted prevalence cautiously.
- If no convincing improvement beyond established baselines, report the negative outcome in appendix rather than force it into the primary contribution.

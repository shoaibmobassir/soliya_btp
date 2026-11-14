# Stage 4 — paired metrics, CIs, inferential discipline

Implement `src/metrics.py`, `src/bootstrap.py` and pytest fixtures in the actual experiment repo.

**Definitions** for binary primary task:
- `UFR` on valid label-preserving pairs = sum(ŷ(anchor) != ŷ(edit)) / n_valid_preserve_pairs.
- `CCAR` on valid label-changing pairs = sum(ŷ(anchor)==y(anchor) AND ŷ(edit)==y(edit)) / n_valid_change_pairs.
- `JointAccuracy` likewise on every valid pair; direction-aware adaptation and raw flip rate secondary.
- Annotator disagreement (entropy or raw vote fractions) is descriptive, not an automatic measure of inherent uncertainty.
- Add majority-class and target-only baselines; report CCAR for target-only as structurally limited on label-flip pairs, not a fair stand-alone superiority claim.

**Uncertainty:** resample clusters by originating conversation (all variants together). If repeated targets per conversation, cluster accordingly. Generate CI for each metric and paired DIFFERENCES under identical resamples. Fix bootstrap seed. Choose >=2000 reps for final study. Avoid CI claims with tiny n; report effective n and variation. Consider two-stage bootstrap or hierarchical analysis for sampled annotators, where feasible.

**Pre-registration:** choose primary models/comparisons and meaningful effect threshold before held-out tests. Correct multiple primary contrasts via Holm, and explicitly label secondary analyses exploratory.

**Tests:** perfectly correct oracle -> UFR=0, CCAR=1; constant label -> UFR=0 but CCAR=0 on true flipping pairs; reversed answers -> failure; duplicate variants grouped correctly; unequal clusters; missing predictions rejected; probabilities in [0,1]; no denominator zero silently converted to 0 (report undefined/NA).

**Reporting:** Tables with n, point estimate, 95% CI, paired comparison, interval and p-value where justified; no significance claims from overlapping individual CIs alone. Show accuracy/recall/FPR simultaneously; include pair-level error analysis and human ambiguity sensitivity checks.

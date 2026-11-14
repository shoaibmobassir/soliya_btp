# Study protocol v0.1 — TO BE FROZEN AFTER PILOT

## Research problem
Current binary or 14-way companion-harm detectors may vary with context even when such variation is unjustified, or fail to vary when relevant evidence changes. The study asks whether these behaviors can be measured with human-validated paired contexts holding the **target AI utterance exactly fixed**.

## Main estimands
- **UFR (unjustified flip rate):** among human-validated *label-preserving* pairs, fraction with differing discrete model predictions. Lower is better; report paired joint accuracy too to prevent constant-label gaming.
- **CCAR (correct contextual adaptation rate):** among human-validated *label-changing* pairs, fraction in which BOTH arm predictions match independent gold labels. Higher is better. Report direction-aware and raw flip rates secondarily.
- **Paired joint accuracy:** fraction of pairs where both predictions correct, for each pair family.
- **Gold validity:** validation pass rate among attempted edits, agreement/confidence distributions, coherence ratings.

## Research questions / falsifiable hypotheses
RQ1: Do real and altered contexts induce unjustified flips? H1: at least one tested model shows nonzero UFR with uncertainty interval inconsistent with zero on verified neutral perturbations. A small nonzero may not be scientifically important; preregister practical-effect threshold after pilot.
RQ2: Can detectors correctly update under validated label flips? H2: full-context models achieve CCAR above target-only and trivial class-prior baselines on balanced verified pairs. Target-only cannot adapt when target fixed; report this as structural ceiling, not an impressive trained-model comparison.
RQ3: Are results robust to model families/context perturbation families? H3: model rankings or failures vary across families; null differences are publishable.
RQ4 (optional): Can a budget-aware context selection policy improve risk-cost tradeoffs after calibration under equal units? Test only if pilot and main audit justify it.

## Benchmarks
CompanionHarm official conversation-disjoint train 4222/1268 conversations, dev 1403/423, test 1391/420 utterances/conversations. Confirm against local source and upstream README. CompanionHarm original 14 labels, derive binary harmfulness transparently. Context availability flags are required. AICompanionBench 2123 conversation-level examples, 9 reported categories including no-harm; cannot be silently recast as utterance labels. Assess rights and provenance before access or redistribution.

## Sampling and design
Pilot: ~50 source target utterances, two edits each (100 edited conditions) plus originals; target quotas, not observed counts. Full proposal: ~300 original targets, two edits per target, ~900 conditions, 3 human ratings each (~2700 ratings), after pilot-based power/precision analysis. Stratify on harm category, original annotation agreement, context availability, model correctness; include a probability sample to permit less biased population interpretation.

Edit types: context-relevant label change, irrelevant label-preserving edit. Families: fiction/real-world frame; relationship boundaries and consent; risk-relevant disclosure; emotionally laden distractor; evidence position/distance. Keep fixed target bytes/hash. Validate turn consistency, realistic dialogue, risk interpretation, edit intent; exclude invalid edits from primary metrics and disclose attrition.

## Human annotation
Blind to paired arm/intent; randomized order, multiple independent raters, pre-set adjudication rules; separately ask harm label, confidence, evidence span(s), coherence, intent validity; preserve all votes. Do not assume unanimous or majority labels uniquely establish objective real-world harm. Provide distress resources/support plan to annotators where appropriate; confirm institution approval.

## Splitting / avoidance of leakage
Group by originating conversation; additionally group synthetic variants and template families as appropriate. Build and freeze development vs evaluation subsets before training routing models. Do not use existing official test examples in feature-development, model selection, edit selection, or prompt tuning. Prefer drawing edit development from train/dev and a once-held-out evaluation set from official test only with appropriate preregistration; do not reuse exposed baseline test statistics for new confirmatory model selection. Report exploratory vs confirmatory status clearly.

## Primary analysis
Two-sided 95% conversation-cluster bootstrap CIs (>=2000 reps for finalized analysis if feasible) for UFR, CCAR and model paired differences. Repeated seeds only for stochastic retraining. Multiplicity: preregister primary family, Holm correction for multiple primary contrasts, secondary results exploratory. Show per-category sample sizes and uncertainty. Freeze thresholds and mapping before test.

## Scope limit
Predicting expert-annotated harm categories is not demonstrating real-world psychological harm; no claims of clinical efficacy, intervention success, or production readiness. Negative results remain publishable only if methodological rigor and evidence are strong.

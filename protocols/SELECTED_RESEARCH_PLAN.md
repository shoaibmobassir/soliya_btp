# Selected research plan

This plan incorporates the research decision supplied by the project owner. Experiment B is the main empirical contribution. Experiment A measures contextual sensitivity and informs feasibility. Experiment C is conditional on validated contextual failures and a meaningful common cost budget.

## Cohorts and exposure

On 2026-11-12 the project owner reported no prior use of the official CompanionHarm test split and no independent pilot ratings. Local data authorization applies to the pinned CompanionHarm release. Apply the private exclusion manifest to all derived cohorts. The verified exclusions cover 9 train, 3 development, and 8 test conversations. The local model runner accepts train and development only. Keep the official test split sealed for confirmatory scoring until G4, with all variants grouped by source conversation and a prospective template-family holdout where feasible.

## A. Controlled context diagnostics

Train matched balanced word unigram and bigram TF-IDF logistic regressions on the original train labels. Fit one model on the reply alone and the other on the full prefix plus reply. Compare these fits on unaltered development records. The reference labels come from the source corpus and may use a wider annotation view.

Hold the full model fixed for removal, last user turn, last three turns, shuffled order, mismatched length, neutral padding, user turns, and prior AI turns. A length-matched neutral replacement is an additional diagnostic. Report prediction changes relative to the full input, input-change coverage, and conversation-clustered intervals. The labels of altered contexts require human judgment before computing their accuracy. Keep neutral padding and neutral replacement distinct. The former appends a synthetic user turn to the existing prefix. The latter replaces the prefix with synthetic words.

The local development run covers the lexical baseline. Before a wider model comparison, recover or retrain the transformer using traceable train-only inputs and development selection. Use five seeds for stochastic training. Optional instruction-tuned evaluation must use permitted local inference. Record hyperparameter budgets, labels, metrics, model hashes and fixed thresholds before the held-out run.

## B. Human-validated fixed replies

Screen 50 development source replies. The queue contains 25 probability-sampled sources and 25 enriched sources from distinct conversations. Eligibility in the sampling frame requires two prior turns and at least one user turn. The author then verifies whether a coherent edit can be made. Retain the original and attempt one relevant edit and one matched distractor edit per source. A source can be ineligible and an edit can be unconstructible.

Use a focused boundary judgment for the main feasibility analysis. Collect a separate broad focal-reply harmfulness judgment to assess the other intervention families. Report these outcomes by rubric and family. Generalizing the boundary result requires adequate human-validated cases in the corresponding strata.

| Family | Minimum candidate operation | What the blinded ratings must establish |
| --- | --- | --- |
| Fiction versus real interaction | Change one role-marked turn that establishes the frame. | The reply's meaning and safety judgment under each frame. |
| Consent and boundary | Change one turn governing permission for the focal action. | Scope, current applicability, and the resulting judgment. |
| Relevant vulnerability | Change one disclosure turn while preserving reply plausibility. | Whether the disclosed fact materially changes the appropriate judgment. |
| Irrelevant emotional distraction | Replace one turn or insert a single distractor turn. | Whether the distractor changes the label or introduces a competing interpretation. |
| Evidence position and distance | Move one intact turn while preserving the remaining order. | Whether chronology, scope, plausibility, and the judgment survive the move. |

Record a fresh judgment on every original and edited arm. Assign a reply-only diagnostic to up to ten screened eligible sources. For any source, each reviewer sees one arm. With three ratings per condition this requires nine distinct reviewers for three-arm sources and twelve if the reply-only arm is included. Treat reply-only labels as a separate visibility diagnostic.

Expand toward 300 sources and 600 edits only after the pilot shows meaningful feasibility. At three ratings per condition the main proposed study has 2,700 initial ratings. Define success and stop rules before examining human results. Review validation yield, both change directions, construct realism, annotation disagreement, and expected precision with conversation clusters. Retain intended and observed relations independently. G4 freezes the final cohorts, models, contrasts and inference before test scoring.

## C. Conditional routing

Proceed only if B reveals replicable, practically meaningful failures and provides enough development cases. Compare target-only, acquiring context, and referring to human review. Use out-of-fold training predictions to estimate context need. Compare uncertainty, disagreement, random, learned context need, and learning-to-defer baselines at matched budgets. Total cost includes initial target inference, context inference, human review, and routing overhead. Report computational cost, review workload, miss rate and safe false-positive rate separately. Use measured reviewer performance where available. Explicit reviewer-error scenarios support simulation when such measurements are unavailable.

## External validation and release

AICompanionBench remains metadata-only pending an explicit corpus grant and a source and cross-corpus overlap audit. Its conversation labels were finalized with access to model predictions. Freeze a conservative label mapping and alternative aggregation rules before using it. Keep conversation transfer distinct from utterance evaluation. Both datasets originate from Replika, and the source terms and populations constrain generalization. Use the independent scientific reviews and the claim ledger to assess readiness before submission.

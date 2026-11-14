# Stage 6 — external comparison and label crosswalk

AICompanionBench (reported 2123 conversations; 9 classes including no-harm) differs in annotation unit from CompanionHarm (utterance-level). These are both Replika-derived, so do NOT call cross-dataset transfer cross-platform generalization.

1. Verify access and schema/license. Compare metadata, screenshots/OCR artifacts and near-duplicate conversations across corpora. Exclude duplicates from transfer and transparently report matching threshold sensitivity.
2. Keep separate within-dataset primary evaluation. For transfer, define a binary harmonization plus a conservative class crosswalk and at least one alternative mapping BEFORE seeing transfer labels/results.
3. Aggregate CompanionHarm to conversation level only when scientifically justified; pre-specify `any harmful`, `majority harmful`, and a label-boundary sensitivity analysis. The aggregation is not equivalent to direct conversation labeling. Never pretend the individual utterance inference task is identical.
4. Verify AICompanionBench selection/annotation details (LLM pre-filter, human revision) and atypical safe distribution. Report source selection bias and taxonomy mismatches.
5. Compare with CompanionSafe only under matching protocol. Published benchmark accuracy must not be placed alongside binary macro-F1 as if directly comparable.
6. If dataset rights/provenance are unresolved, mark external results as blocked and maintain main-paper study on legally permitted corpus. Do not build a false 'two-corpus' claim.

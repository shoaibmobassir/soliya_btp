# Review objections and responses

| Concern | Response | Remaining evidence |
| --- | --- | --- |
| Fixed-target context sensitivity and paired scoring have substantial precedent. | Narrow the main question to whether earlier explicit, scoped boundary evidence changes the correct judgment of an identical companion reply. Cite ConCI, DiaSafety, COBRA Frames, MTAG-Bench and No Convo!. | Obtain independent gold and show that the scoped contrasts survive feasibility review. [Novelty review](../agents/novelty_validator.md) |
| Original harm labels use a wider context and a broader rubric. | Use those labels for the exploratory lexical audit. Require new ratings for originals, edits and a reply-only subset. Add distinct focal-boundary and broad harm judgments. | Human approvals, scope and coherence checks, and locked adjudication. [Methods review](../agents/methodology_reviewer.md) |
| Altered inputs can be no-ops or change the correct label. | Report changed-rendering counts and prediction flips. Add neutral padding and whole-prefix replacement as distinct probes. | Independent human labels for claims about justified changes. [Development aggregate](CONTEXT_AUDIT_DEV.json) |
| Small or imbalanced samples make intervals unstable. | Resample whole conversations with common draws across models. Expose per-relation support, undefined scores and degenerate intervals. | Validation yield, direction balance, and predeclared practical thresholds. [Statistics review](../agents/statistics_reviewer.md) |
| Cross-split IDs miss duplicated text, and external labels have another unit. | Apply local exclusions to all derived cohorts. Use AICompanionBench only if a grant, cross-corpus checks, and a locked conversation-level crosswalk become available. | Human-review approval and external rights remain separate. [Ethics review](../agents/ethics_release_reviewer.md) |

The independent follow-up reviewed public artifacts and exploratory results. Final reproducibility review follows the held-out analysis.

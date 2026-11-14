# Stage 0B data audit — 2026-11-12

**Local pinned audit and derived split policy complete.** The script verified the actual CSVs and found text overlap across splits. The private exclusion manifest defines eligibility for derived cohorts. The owner reported no prior use of the official test split. Confirmatory scoring remains sealed until protocol freeze. [Aggregate audit](COMPANIONHARM_AUDIT.json) · [Cohort policy](../protocols/SELECTED_RESEARCH_PLAN.md)

## CompanionHarm

| Split | Upstream README AI rows | Upstream README conversations | Observed locally |
| --- | ---: | ---: | --- |
| Train | 4,222 | 1,268 | 4,222 rows, 1,268 conversations |
| Dev | 1,403 | 423 | 1,403 rows, 423 conversations |
| Test | 1,391 | 420 | 1,391 rows, 420 conversations |
| Total | 7,016 | 2,111 | 7,016 rows, 2,111 conversations |

The local totals agree with the upstream release. Both conversation and utterance ID intersections were empty across all splits. [Aggregate audit](COMPANIONHARM_AUDIT.json) · [Pinned README](https://github.com/HanMeng2004/CompanionHarm/blob/ed96c1c15818b2a2663192b4ac9655ae5e915d05/README.md#benchmark-design)

The local CSVs match the documented schema. Prefixes use line-initial User and Replika speaker markers, and the target field has its own Replika marker. All parsed prefix lengths and nested traces agreed with the recorded focal turn positions. The preprint describes humans seeing the complete conversation during annotation while detection receives the preceding context. Fresh prefix-only human judgments are therefore needed on **all** arms to establish a paired gold relation. [Pinned data card](https://github.com/HanMeng2004/CompanionHarm/blob/ed96c1c15818b2a2663192b4ac9655ae5e915d05/DATA_CARD.md) · [Paper, Data Annotation and Experimental Setup](https://arxiv.org/html/2608.25377)

Expected closed labels are Antisocial behavior, Hate speech, Control, Disregard, Infidelity, Manipulation, Mis/Disinformation, No harmful behavior, Physical aggression, Privacy violations, Self-harm & Suicide, Sexual misconduct, Substance abuse and Verbal abuse. The prospective deterministic binary mapping uses No harmful behavior → safe and the other 13 valid majority labels → harmful. Quarantine missing, out-of-vocabulary and unresolved labels. Preserve 14-way labels, vote totals and provenance separately. The card says unresolved three-way disagreements were excluded from the benchmark release and that a dissenting Others exists only in archived minority metadata. The preprint describes a full annotator-level dataset, which this pinned artifact does not supply. [Pinned data card](https://github.com/HanMeng2004/CompanionHarm/blob/ed96c1c15818b2a2663192b4ac9655ae5e915d05/DATA_CARD.md)

The preprint abstract reports seven LLMs and the pinned release README describes eight systems and 24 archived model/prompt conditions. The sources have separate identifiers and need reconciliation before any baseline comparison. The notebook in the inventory cannot establish prior split integrity, checkpoint identity or run lineage. [Preprint v1](https://arxiv.org/abs/2608.25377v1), [Pinned README](https://github.com/HanMeng2004/CompanionHarm/blob/ed96c1c15818b2a2663192b4ac9655ae5e915d05/README.md)

## AICompanionBench

The paper describes 2,123 **whole Replika conversations** and one category per conversation. The categories are sexual behavior, antisocial behavior, physical aggression, verbal aggression, substance abuse, self-harm and suicide, control, manipulation and no-harm (safe in README). §§III-A–B report a funnel based on initial model judgments and selection enriched for unsafe candidates. One trained annotator provided initial ratings and finalized labels with access to the 20-model results. These choices condition the sample and can affect evaluation against judges whose outputs informed labels. Keep whole-conversation validation exploratory and conditional on provenance and overlap approval. An utterance-level crosswalk would require separate unit-appropriate gold. The repository currently lists a CSV, while the preprint points to an XLSX. The file-level schema, version equivalence and row counts remain pending. [Paper §§III–IV](https://arxiv.org/html/2606.04867), [Pinned README](https://github.com/anonymousresearcher2026/AICompanionBench/blob/4dbc9ec2b3027a0049094eb3cfda82390bcf1c74/README.md)

## Local custody and future checks

1. A local custodian records the approved exact version, hashes original bytes with SHA-256 before and after a read-only audit, and confirms schema, role structure and split label consistency. Retain private manifests and export aggregate summaries only. Protect official test contents from anyone designing interventions, models or the primary protocol. Where the institutional access plan permits a split-integrity audit before freeze, a designated custodian runs it and shares only a gate verdict and non-item aggregates.
2. Recompute counts and unique conversations per split. Check duplicate IDs within and across splits, full-row duplicates, exact and near-duplicate conversations across splits, mixed-split variants, and context leakage. Follow [the overlap audit](OVERLAP_AUDIT.md) for attribution of flags.
3. Confirm the proposed exclusions and document prior exposure before assigning data to the final evaluation. Verify byte-invariant targets when the pilot pairs are constructed.

## Implemented custodian checks

With an approved read-only copy, run the following from the project root in the custodian's authorized environment. Retain the report locally for review.

```sh
python3 -B scripts/audit_companionharm.py --split-dir /approved/local/data/splits
```

The script verifies split bytes against pinned Git blob IDs and sizes before parsing, computes whole-file SHA-256 before and after, and compares observed row and conversation counts against the manifest. It checks the data card schema, target speaker, split fields, label and agreement values, duplicate rows and keys, and all cross-split ID intersections. The report includes aggregate exact/normalized context-target flags, cross-split normalized text-pair intersections and blank context counts by turn. It emits no text rows, source IDs, or row fingerprints. Full-row duplicates are comparisons of parsed field values. Normalization uses NFC and collapsed whitespace. The text flags require manual review.

Exit status 0 means the base integrity checks found no blocking issue. Status 1 reports blocking findings. Status 2 gives a fixed diagnostic for an unreadable, unpinned, changed or unparseable input. The extended audit is run as `python3 -B -m scripts.audit_conversation_overlap --split-dir PATH`. It adds role-aware reconstruction and exact and fuzzy text comparisons. Its optional `--write-private-exclusions` flag stores candidate IDs in an owner-only directory beside the inputs. The base and extended checks have been run on the pinned release. [Audit implementation](../scripts/audit_conversation_overlap.py) · [Overlap findings](OVERLAP_AUDIT.md)


## Reviewer coverage and external candidates

On 2026-11-13 the verified local loader returned 4,185 train replies and 1,393 development replies after overlap exclusions. Development contained 13 of the 14 published labels. The selected 50 development sources had 2–11 turns preceding their focal reply, including 36 with more than two. These are context counts, independent of screening and edit eligibility. No test rows were reopened. [CompanionHarm release and terms](https://github.com/HanMeng2004/CompanionHarm/blob/ed96c1c15818b2a2663192b4ac9655ae5e915d05/README.md#licensing-and-terms-of-use)

| Candidate | Fit for this study | Current disposition |
| --- | --- | --- |
| CompanionHarm | Naturally occurring dialogue with labels for a specific companion reply. All preceding turns form the context for that reply. | Active development source. Keep the selected 50 in the pilot; no public transcripts. Show the longest available trace to the coordinator and only the assigned evidence to each reviewer. [Paper, experimental setup](https://arxiv.org/html/2608.25377v1) |
| AICompanionBench | 2,123 whole conversations with nine conversation-level labels. This is a different unit from a fixed reply, and both datasets originate from Replika. | Metadata only pending rights, overlap and a separate evaluation protocol. [Primary paper](https://arxiv.org/html/2606.04867) |
| CompanionSafe | CompanionEval uses simulated personas and attack trajectories. CompanionGuard's artifact has turn-localized targets derived from benchmark runs. | Candidate for separate synthetic stress testing. Establish file-level provenance, overlap, and independent labels for the study rubric before using it as evaluation evidence. [Repository](https://github.com/AI45Lab/CompanionSafe) |
| MIRROR-Eval | Crisis-focused, synthetic persona scenarios with a separate rubric. | Gated artifacts and specialized population. Candidate for a separate crisis evaluation after reviewing access conditions and reviewer safeguards. [Dataset card](https://huggingface.co/datasets/imda-biztech/MIRROR-Eval) |

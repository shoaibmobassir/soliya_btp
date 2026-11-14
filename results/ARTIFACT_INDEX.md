# Stage 0 artifact index — 2026-11-12

## Repository guide

- [README](../README.md) explains setup, review workflows, data restrictions, and current study status.

## Shared practice responses

- Practice response storage is connected to the hosted practice site. The private local export target is `private_data/practice_review/responses.csv`.

## Expanded reviewer practice

- [Fictional practice cases](../pilot_review_preview/cases.json), [adapted CompanionHarm harm guide](../pilot_review/harm_guide.json), and [dataset fit audit](DATA_AUDIT.md#reviewer-coverage-and-external-candidates).

## Reviewer practice

- [Public fictional practice site](https://context-evidence-review-practice.aurorahen128.chatgpt.site) and [practice asset builder](../pilot_review_preview/build.py).

## Pilot review workspace

- [Launch and reviewer setup](../protocols/PILOT_REVIEW_UI.md), [local server](../scripts/pilot_review.py), and [interface](../pilot_review/index.html).

## Selected study and current progress

- [Progress bar](PROGRESS.md) and [selected research plan](../protocols/SELECTED_RESEARCH_PLAN.md).
- [Development audit aggregate](CONTEXT_AUDIT_DEV.json), [first-run archive](CONTEXT_AUDIT_DEV_V1.json) and [generated development tables](../paper/development_tables.tex).
- [Pilot queue summary](PILOT_QUEUE.json), [blinded packet tool](../scripts/prepare_blind_pilot.py), and [human evidence intake](../scripts/summarize_human_pilot.py).
- [Colab-ready synthetic metrics notebook](../notebooks/paired_metrics_demo.ipynb) and [review objections](REVIEWER_OBJECTIONS.md).
- [Development data loader](../scripts/development_data.py), [context audit runner](../scripts/run_context_audit.py), [fixed audit configuration](../configs/context_audit.json), [pinned requirements](../configs/context_audit_requirements.txt), and [table renderer](../scripts/render_development_tables.py).
- [Pilot queue builder](../scripts/create_pilot_queue.py), [local draft runner](../scripts/draft_pilot_locally.py), [draft assembler](../scripts/assemble_pilot_drafts.py), and [paired metric implementation](../scripts/paired_metrics.py).
- [Local pilot case editor](../scripts/edit_pilot_case.py) for author screening in a terminal editor.
- [Pilot report](PILOT_REPORT.md), [boundary drafting aggregate](PILOT_DRAFTING.json), and [broader drafting aggregate](PILOT_DRAFTING_BROAD.json).
- [Pilot screening status](PILOT_SCREENING.json), [validation report](PILOT_VALIDATION.md), and [status generator](../scripts/pilot_screening_status.py).

## Local audit and manuscript

- [Open manuscript source](../paper/main.tex), [bibliography](../paper/references.bib), and [generated audit tables](../paper/audit_tables.tex).
- [Aggregate audit](COMPANIONHARM_AUDIT.json), [conversation overlap code](../scripts/audit_conversation_overlap.py), and [table renderer](../scripts/render_audit_tables.py).
- [Blinded pilot packet](../protocols/BOUNDARY_PILOT_PACKET.md), [claim-to-evidence ledger](CLAIM_EVIDENCE_LEDGER.csv), and [reproducibility checklist](REPRODUCIBILITY_CHECKLIST.md).

| Artifact | Contents |
| --- | --- |
| [Status](STATUS.md) and [decisions](DECISIONS.md) | Session checks, gate disposition and next task |
| [Input inventory](INPUT_INVENTORY.md) | Scoped local discovery, notebook hash and remote artifact locations |
| [Prior-art matrix](PRIOR_ART_MATRIX.csv) and [source ledger](SOURCE_LEDGER.md) | Primary method comparisons, search coverage and unverified items |
| [Novelty verdict](NOVELTY_VERDICT.md) and [validation synthesis](VALIDATION_SYNTHESIS.md) | Revised candidate contribution, stop criteria and independent findings |
| [Relational-evidence design](../protocols/RELATIONAL_EVIDENCE_DESIGN.md) | Draft paper question, focal label, matched comparison and analysis |
| [License ledger](LICENSE_LEDGER.md) | Component-specific terms, project scope and approval intake |
| [Data audit](DATA_AUDIT.md) and [overlap audit](OVERLAP_AUDIT.md) | Upstream reports, unobserved quantities, authorized custodian procedure |
| [Source manifest](../data/source_manifest.json) | Pinned remote revisions, Git object metadata and verified documentation SHA-256 values |
| Independent reviewer reports | [Novelty](../agents/novelty_validator.md), [methodology](../agents/methodology_reviewer.md), [statistics](../agents/statistics_reviewer.md) and [ethics and release](../agents/ethics_release_reviewer.md) |
| [Stage 0 checks](../tests/test_stage0_evidence.py) | Offline tests for manifest semantics and literature evidence coverage |
| [Local CompanionHarm audit](../scripts/audit_companionharm.py) and [fixture tests](../tests/test_companionharm_audit.py) | Read-only pinned split checks and aggregate reporting, tested with authored temporary CSVs |

The index covers documentation, source metadata and audit checks. Experiment artifacts and corpus-derived measurements remain pending.

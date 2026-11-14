# ContextEvidenceBench

A research package for studying how conversation context changes safety judgments of a fixed AI-companion reply. It contains study protocols, data audits, paired metrics, a blinded human-review workflow, a fictional practice app, and exploratory development analysis.

Novelty is a hypothesis to be checked. See the [prior-art verdict](results/NOVELTY_VERDICT.md), [source ledger](results/SOURCE_LEDGER.md), and [validation synthesis](results/VALIDATION_SYNTHESIS.md).

## Current status

The project audited a pinned CompanionHarm release locally and ran an exploratory lexical analysis on train and development data. A 50-source development pilot was selected, but human screening and an approved independent review plan remain outstanding. The practice website uses fictional cases. Its responses are not pilot annotations. The study protocol is not frozen and no new confirmatory held-out experiment is reported.

Check [status](results/STATUS.md), [pilot validation](results/PILOT_VALIDATION.md), and [decisions](results/DECISIONS.md) for current gates and limitations.

## Quick start

The tests use synthetic fixtures and do not require the private corpus.

```bash
git clone https://github.com/shoaibmobassir/soliya_btp.git
cd soliya_btp
python3 -B -m unittest discover -s tests -q
```

For a fictional local reviewer demonstration:

```bash
python3 -B -m scripts.pilot_review --demo
```

Open the coordinator URL printed in the terminal, expand **Individual reviewer invitations**, and open a demo link. Demo storage is temporary. The existing [public practice site](https://context-evidence-review-practice.aurorahen128.chatgpt.site/) uses fictional conversations and shared practice-response storage. Its responses are not study annotations.

The local authoring interface uses privately held, pinned development data and the prepared queue. On an authorized machine with those inputs present, run `python3 -B -m scripts.pilot_review` and open the printed coordinator URL. The [review UI guide](protocols/PILOT_REVIEW_UI.md) covers authoring, approval, blinded packets, review, and evidence intake. Remote reviewers require an approved HTTPS route and study plan. The server binds to loopback by default.

## Research workflow

1. Read [AGENTS.md](AGENTS.md), the [study protocol](protocols/STUDY_PROTOCOL.md), [gates](protocols/GATES.md), and the relevant stage in [instructions/](instructions/).
2. Review the [selected plan](protocols/SELECTED_RESEARCH_PLAN.md), provenance and exclusions before accessing data. The corpus, exclusions, checkpoints, reviewer assignments, and raw ratings are privately held.
3. Screen the 50 development sources, author feasible matched edits, and obtain G2 approval before distributing blinded assignments. Follow the [pilot packet](protocols/BOUNDARY_PILOT_PACKET.md).
4. Collect independent ratings, lock them, adjudicate, and review pair quality. Evaluate feasibility and uncertainty before expanding. Model suggestions are not human labels.
5. Freeze the final protocol and holdout policy before confirmatory test access. Continue through the remaining gates in order.

The main paired metrics are unjustified flip rate, correct contextual adaptation rate, and paired joint accuracy. Their definitions and limitations are in the [protocol](protocols/STUDY_PROTOCOL.md) and [metric implementation](scripts/paired_metrics.py).

## Local data and reproducibility

[data/source_manifest.json](data/source_manifest.json) records source revisions, split checksums and provenance. Obtain and use corpus data only within the authorized research scope and place the pinned files and private exclusions under `private_data/` as described in the audit scripts. A fresh clone cannot reproduce real-data runs until those inputs are available. Consult the [license ledger](results/LICENSE_LEDGER.md) and [data audit](results/DATA_AUDIT.md) first.

The development lexical audit requires Python 3.13 and the pinned dependencies in [configs/context_audit_requirements.txt](configs/context_audit_requirements.txt). With authorized inputs in place:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r configs/context_audit_requirements.txt
python -B -m scripts.run_context_audit
python -B -m scripts.render_development_tables
```

The audit saves model and prediction artifacts in private storage. See the [reproducibility checklist](results/REPRODUCIBILITY_CHECKLIST.md) for provenance and limitations. The optional local drafting runner also needs its pinned local model and MLX dependencies.

## Project map

- [protocols/](protocols/) holds the research plan, gates, annotation packet, data dictionary, and review UI setup.
- [instructions/](instructions/) contains stage-by-stage research instructions.
- [scripts/](scripts/) contains audits, pilot preparation, the local review server, metrics, analysis, and table generation.
- [pilot_review/](pilot_review/) contains the interface and an adapted 13-category harm guide. The study must use its approved guide.
- [pilot_review_preview/](pilot_review_preview/) contains independently authored fictional practice cases and the hosted-site source.
- [tests/](tests/) contains synthetic unit tests. [results/](results/) holds reports, ledgers, aggregate diagnostics and status.
- [paper/](paper/) contains the working LaTeX manuscript and generated tables. [agents/](agents/) and [templates/](templates/) contain reviewer reports and research templates.

Build the practice site with `python3 -B pilot_review_preview/build.py`. The server-backed build additionally needs a deployment-specific `.openai/hosting.json` and configured database. Deployment identity and credentials are excluded. Practice responses use shared hosted storage and do not automatically synchronize to a local CSV.

## Privacy and scope

CompanionHarm conversations and derived reviewer evidence are sensitive research material. Do not commit, redistribute, send to external services, or expose them to reviewers without the rights and ethics approvals specified in [AGENTS.md](AGENTS.md) and the [license ledger](results/LICENSE_LEDGER.md). `private_data/` is ignored. Never infer that a context edit preserves or changes a label without independent human confirmation, and do not treat simulated or model-generated ratings as human gold.

The published source includes synthetic examples and aggregate research artifacts. Check upstream licenses, institutional requirements, and study gates before using data or releasing additional artifacts.

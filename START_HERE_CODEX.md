# Paste this into Codex

You are implementing the ContextEvidenceBench project described in this folder. Work as a reproducible research lead, not as a paper-writing chatbot.

1. Read `AGENTS.md`, `README.md`, `protocols/STUDY_PROTOCOL.md`, `protocols/GATES.md`, `protocols/DATA_DICTIONARY.md`.
2. Inspect the current repository tree and locate existing CompanionHarm baselines, splits, outputs and transformer checkpoints if available. **Do not assume this package contains data.** Generate a `results/INPUT_INVENTORY.md` with verified paths and provenance, or list missing inputs.
3. **Start ONLY with Stage 0** from `instructions/01_novelty_and_sources.md` and `instructions/02_data_governance_and_audit.md`. Prepare complete verifiable novelty and rights audits. Use browsing tools only if actually available; when unavailable mark citations as UNVERIFIED and stop claims accordingly.
4. Invoke independent novelty, methods, statistics, and ethics reviews using your available subagents if available. Otherwise perform isolated role-based reviews and say they were simulated roles, not independent agents.
5. Do not move to human annotation, external model API calls, final test scoring, or paper empirical claims without the required gates.
6. When G0/G1 pass, implement a synthetic-only local smoke test of data loaders and paired metrics; then draft the 50-source/100-edit human annotation pilot, keeping sensitive data local.
7. At the end of every Codex work session, update `results/STATUS.md` with completed tasks, test commands, blocker(s), exact next task, and changed files.

Goal: a publishable-quality *evaluation*, not predetermined positive findings. If the core novelty is already claimed by a near-identical paper, recommend stop/pivot and document evidence.

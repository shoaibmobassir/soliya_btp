# Stage 7 — reproducibility / release

Deliver clean research repo with `src/` loaders, transformations, metrics, eval and report generation; `tests/` synthetic fixtures; `configs/` lockfiles; `scripts/` CLI runners; `paper/` manuscript and citation ledger.

Commands to support (implement, do not falsely claim currently exist):
```
python -m src.audit --config configs/experiment.yaml
python -m src.pilot --config configs/experiment.yaml --dry-run
python -m src.baselines --config configs/experiment.yaml --dry-run
python -m src.evaluate --config configs/experiment.yaml --split dev
python -m src.report --config configs/experiment.yaml
pytest -q
```

- Add dependencies pinned to real compatible versions; CPU smoke tests <2 minutes using synthetic text. GPU tests optional with skip markers. Do not download models by default in CI.
- Log versions, hashes, original source metadata, seed, model, tokenization and truncation, training curves, compute, split and threshold/calibration provenance.
- Generate tables and figures **from actual machine-readable results only**; fail loudly if data absent. Model cards and dataset cards require limitations and approved rights.
- Release policy: sanitized hashes/metrics/analysis scripts; raw conversations private. Add automated scanner for obvious PII and prohibited text, but manual review still required.
- Run tests for leakage, target invariance, paired relation, metric denominator, permission checks, reproducible outputs and no fabricated figures.

# Reproducibility checks

Updated 2026-11-13.

- [x] Pinned upstream revision, Git blob IDs, observed counts and SHA-256 values recorded in [source manifest](../data/source_manifest.json).
- [x] Local base, role-aware and fuzzy audits on the official splits. Source hashes and local read-only permissions checked. Aggregate results in [audit JSON](COMPANIONHARM_AUDIT.json).
- [x] Proposed private exclusions verified in memory against all three documented text comparisons. Official split files retain their pinned bytes.
- [x] Offline tests cover source integrity, conversation overlap, blinded assignment, human evidence intake, and paired scoring. The current test count is in [session status](STATUS.md).
- [x] Manuscript tables built from aggregate JSON with `python3 -B scripts/render_audit_tables.py`.
- [x] Current `paper/main.tex` compiled in the desktop LaTeX editor with the bibliography and generated tables.
- [x] Owner-reported absence of prior official test use recorded. All verified exclusions applied to derived cohorts. The locked analysis will document residual text matching limitations.
- [x] Exploratory train and development audit, saved models and prediction checksums, matched bootstrap estimates and generated tables. [Run aggregate](CONTEXT_AUDIT_DEV.json)
- [ ] Authorize human review, complete the pilot and lock the study protocol.
- [ ] Execute and archive transformer and held-out benchmark runs, uncertainty estimates and full claim checks.
- [ ] Complete submission-stage independent review and venue formatting.

Audit command from the project root, with the path set to the authorized local copy:

```sh
python3 -B -m scripts.audit_conversation_overlap --split-dir /path/to/private/splits > results/COMPANIONHARM_AUDIT.json
python3 -B scripts/render_audit_tables.py
```

The optional `--write-private-exclusions` flag writes conversation IDs only to the owner-only split directory. The public report includes counts and source-file hashes. The audited data and exclusion IDs stay in private storage.

Run the lexical development analysis with Python 3.13 in a local environment using [pinned requirements](../configs/context_audit_requirements.txt). From the root:

```sh
python3 -B -m scripts.run_context_audit
python3 -B -m scripts.render_development_tables
python3 -B -m unittest discover -s tests -v
```

The run stores model files, predictions and the pseudonymization key in an owner-only run folder. The aggregate records timestamp, configuration, environment, source and model hashes, split counts and shared conversation bootstrap draws. Probe intervals condition on the fixed input constructions.

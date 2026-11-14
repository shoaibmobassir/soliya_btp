# Session status — 2026-11-13

## Repository preparation

- Prepared a public source repository and setup guide. Restricted data, private reviewer records, credentials, deployment identity, and generated practice builds remain outside the public copy. The synthetic test suite passed 21 tests.
- Real pilot screening and G2 approval remain pending.

## Shared practice responses

- Published persistent shared storage for new fictional practice submissions. Verified a clearly labeled synthetic skipped response arrived in the owner-accessible practice database. Existing browser-only labels and comments were never persisted and cannot be recovered from the service.
- Created an owner-only local CSV for exports. Automatic synchronization from hosted storage to the Mac is not implemented. Real pilot review remains subject to the existing gates.

## Reviewer practice expansion

- Expanded the public practice to 18 independently authored eight-message conversations and the 13-category harm guide. Added optional names and turn-by-turn evidence selection. Verified local export keeps names out of study ratings and preserves each rubric's evidence independently.
- Audited filtered CompanionHarm development data without opening the held-out test. The existing 50 real pilot sources have 2–11 prior turns. Reviewed AICompanionBench, CompanionSafe, and MIRROR-Eval for external fit. No new study data were imported or shared. [Data audit](DATA_AUDIT.md)
- Live review remains pending screening and G2. The planned expansion to about 300 source replies follows the pilot feasibility decision.

## Reviewer experience and remote practice

- Simplified reviewer cases into two plain-language questions, one comment field, and a separate evidence and certainty panel. Verified local label and comment submission and resumption on fictional assignments. Published a public fictional practice site through Sites.
- The live round still requires source screening, recorded G2 approval for remote reviewer access, and the approved HTTPS route. Practice progress is separate from study evidence. [Portal setup](../protocols/PILOT_REVIEW_UI.md)

## Pilot review workspace

- Built a local coordinator UI for all 50 source cases and a separate passwordless reviewer UI with blinded assignments, consent, direct local storage, and a locked evidence export.
- Verified the 50 local case views without emitting conversation text and exercised the review flow using fictional assignments. G2 approval and the approved remote route remain outstanding. No live invitations were issued and no real judgments were added.
- Next: complete human authoring, obtain G2 approval for reviewer access, and follow the [portal setup](../protocols/PILOT_REVIEW_UI.md). Adjudication, pair quality checks, and a feasibility decision precede protocol freeze.

## Pilot workflow review

- Reviewed the local authoring and blinded-rating workflow against the current pilot packet. The author editor now shows the longest available original trace, focal reply, original annotation category, and all candidate suggestions. The source view is read-only. The release may omit later turns.
- Added explicit author accept, modify, reject, and impossible decisions. Every source must have a valid screening decision before reviewer packets can be prepared. The approval record is checked before packet creation.
- Added aggregate screening and pilot-validation reports. They record counts, rejection reason categories, human-review approval and available independent evidence. Current state is 0/50 screened, 0 constructed edits, review approval absent and go/no-go pending.
- Ran `python3 -B -m unittest discover -s tests -q` after each implementation stage. Final result: 21 tests passed. Ran `python3 -B -m scripts.pilot_screening_status` to generate the current reports.
- Blockers: a human must screen and author cases, an approved independent review plan is needed, and independent ratings and adjudication must exist before the pilot feasibility criteria can be assessed. No human decisions, labels, or held-out results were fabricated.
- Exact next task: a human author runs `python3 -B -m scripts.edit_pilot_case --case P001` locally and works through all 50 cases. Run the screening status command after updates. Once the review plan is actually approved, record the approval and prepare blinded packets.
- Changed files: `scripts/edit_pilot_case.py`, `scripts/prepare_blind_pilot.py`, `scripts/pilot_screening_status.py`, `tests/test_edit_pilot_case.py`, `tests/test_blind_pilot.py`, `tests/test_pilot_screening_status.py`, `protocols/BOUNDARY_PILOT_PACKET.md`, `results/PROGRESS.md`, `results/DECISIONS.md`, `results/ARTIFACT_INDEX.md`, `results/PILOT_SCREENING.json`, `results/PILOT_VALIDATION.md`, and this status file.

## Pilot authoring handoff

- Added a local terminal editor for one private pilot case at a time. It checks immutable source fields and target bytes against the verified development release, validates completed edits, and saves an owner-only queue. Added a regression test for source and suggestion preservation.
- Ran `python3 -B -m unittest discover -s tests -q` (18 passed), `python3 -B -m scripts.edit_pilot_case --help`, and compiled `paper/main.tex` successfully using the desktop editor.
- All 50 source decisions remain pending. G2 approval and independent human judgments remain outstanding. No pilot labels or held-out model scores were produced.
- Exact next task: a human author runs `python3 -B -m scripts.edit_pilot_case --case P001` from the project root and screens the local cases using the pilot packet. Complete the approved independent review process before generating reviewer assignments.
- Changed files: `scripts/edit_pilot_case.py`, `tests/test_edit_pilot_case.py`, `protocols/BOUNDARY_PILOT_PACKET.md`, `results/ARTIFACT_INDEX.md`, and `results/STATUS.md`.

**■■■■■□□□□□ 50% · 5 of 10 primary milestones complete.** [Milestone definitions and progress](PROGRESS.md)

## Selected research plan and development execution

- Reviewed the supplied decision and verified the closest source claims. Four independent follow-ups updated the novelty, methods, statistics, and ethics reports. The matrix covers 34 sources. The revised focal-boundary design remains a feasibility candidate.
- The owner reported no prior official test use and no independent pilot ratings. Adopted the verified exclusions for derived cohorts. G0/G1 are cleared for CompanionHarm local development work. The test cohort remains sealed for confirmatory scoring until G4. The scope includes local corpus analysis and model drafting. G2 human approval remains outstanding.
- Completed the lexical development audit on 4,185 filtered train and 1,393 filtered development replies. Macro-F1 was 0.610 with the reply alone and 0.614 with full context. The paired 95% interval for the difference was [-0.030, 0.038]. The fixed-model probe rates describe prediction changes on unvalidated inputs. Saved the initial run and reran with distinct padding and replacement probes, changed-rendering counts, and stronger input checks. [Development aggregate](CONTEXT_AUDIT_DEV.json)
- Selected 50 private development sources from distinct conversations with 100 intended edit slots. Implemented family-aware checks, blinded assignment, a reply-only subset, human evidence intake, and paired metrics with clustered uncertainty. [Pilot packet](../protocols/BOUNDARY_PILOT_PACKET.md)
- Ran two bounded offline drafting passes with a pinned 4-bit Qwen3-1.7B checkpoint. Retained one boundary suggestion and ten broader suggestions after structural checks. Ran `python3 -B -m scripts.assemble_pilot_drafts` and verified 50 distinct source IDs, exact target hashes, pending approval states, and owner-only permissions. No suggestions have human approval or ratings. [Pilot report](PILOT_REPORT.md)
- Integrated the selected design, measured audit and exploratory results into the existing manuscript. Generated LaTeX tables directly from JSON. The desktop compiler succeeded. [Manuscript](../paper/main.tex)
- Verification: `python3 -B -m unittest discover -s tests -q` passed 17 tests. Both development classification summaries were independently recomputed from saved predictions and model hashes were verified. The standalone notebook executed on invented fixtures locally.
- Next dependency: a human author screens `private_data/boundary_pilot/review_drafts.jsonl` for scope, coherence and private review eligibility, and completes or rejects each edit slot. Obtain an approved local independent review process, then assign, lock and adjudicate pilot ratings. Confirmatory scoring, full-scale benchmark construction, routing, external validation and submission depend on their respective gates.
- New implementation and artifacts are listed in the [artifact index](ARTIFACT_INDEX.md). The substantive current edits also include `paper/main.tex`, `paper/references.bib`, `protocols/BOUNDARY_PILOT_PACKET.md`, the data and overlap reports, the source and claim ledgers, and the four reviewer reports.

## Local audit and manuscript session

- The project owner confirmed local use. Downloaded and verified the three pinned CompanionHarm split files into owner-only, ignored storage. No corpus content was sent to an external service. Recorded observed counts and hashes in `data/source_manifest.json`.
- Measured 7,016 annotated replies and 2,111 conversation IDs. All official ID intersections were empty. Train–test shared four exact and two near-matching traces under the documented screen. Verified in memory that proposed private exclusions (9 train, 3 development, 8 test conversation IDs) remove every cross-split match found by the screen.
- Drafted the audit and study protocol in the open `paper/main.tex`, with bibliography and tables generated from aggregate JSON. Prepared the blinded pilot packet and claim-to-evidence ledger.
- Applied the scope, critical review and verification steps from the requested gstack guidance at revision `4414f4cc9377a9df06c7847433fe567ba6398aa8` to the audit and paper. The full software release workflow was outside the research task.
- Ran `python3 -B -m unittest discover -s tests -v` (10 passed), `python3 -B -m scripts.audit_conversation_overlap --split-dir <private path> --write-private-exclusions`, and `python3 -B scripts/render_audit_tables.py`. Verified source hashes, owner-only permissions and removal of flagged overlap with an in-memory recheck. Checked the LaTeX source with the desktop compiler.
- **G0:** CompanionHarm local rights addressed per owner confirmation. The focused design remains a revised feasibility candidate. **G1:** source audit complete and exclusion list prepared, with the derived split policy and legacy holdout exposure pending. **G2/G3:** independent human review plan and real judgments pending. Model scoring and empirical detector conclusions remain pending.
- **Next task:** settle the exposure record and finalize the derived cohort policy. Once G1 clears, implement the paired-metric smoke test. Arrange the approved blinded human pilot and obtain independent judgments before using any edit relation as gold.
- Changed files in this session: `.gitignore`, `data/source_manifest.json`, `scripts/audit_conversation_overlap.py`, `scripts/render_audit_tables.py`, `tests/test_conversation_overlap.py`, `paper/main.tex`, `paper/references.bib`, `paper/audit_tables.tex`, `protocols/BOUNDARY_PILOT_PACKET.md`, `results/COMPANIONHARM_AUDIT.json`, `results/CLAIM_EVIDENCE_LEDGER.csv`, `results/REPRODUCIBILITY_CHECKLIST.md`, `results/LICENSE_LEDGER.md`, `results/DATA_AUDIT.md`, `results/OVERLAP_AUDIT.md`, `results/INPUT_INVENTORY.md`, `results/ARTIFACT_INDEX.md`, `results/DECISIONS.md`, and this status file. The pinned raw files and private exclusion list live under the ignored directory.

## Earlier guidance session

- Reviewed the study gates, rights ledger, reproducibility and manuscript instructions, and existing LaTeX sources to prepare the research workflow.
- Ran `python3 -B -m unittest discover -s tests -q`. All 8 tests passed. Checked for `latexmk`, `pdflatex`, and `bibtex`. No commands were found on the local PATH, so PDF compilation remains unverified.
- Blockers remain G0 rights and G1 source and split verification. The LaTeX document is a placeholder and the bibliography needs citation verification.
- Exact next task is to document the authorized scope for CompanionHarm and obtain the approved pinned split files for local custodian checks. Then complete the remaining G1 overlap and exposure audit.
- Changed file in this session: `results/STATUS.md`.

At that point G0 and G1 were blocked and the prior-art verdict was REVISE.

## Earlier Stage 0 follow-up

- Drafted the specific paper question and label for detecting whether the focal companion reply crosses an explicit user boundary that applies at the time of reply. Specified the matched edits, blind gold labels, and a comparison between two detectors that receive the same visible prefix. Reran the focused duplicate search and added four primary texts to the 30-source matrix. [Design](../protocols/RELATIONAL_EVIDENCE_DESIGN.md) · [Focused novelty check](NOVELTY_VERDICT.md#focused-follow-up-explicit-user-boundaries)
- Implemented a read-only custodian audit of pinned CompanionHarm CSVs. Tests used only independently authored temporary fixtures and covered release identity, immutable bytes, split leakage, label mapping and text-free diagnostics. Actual source headers, bytes and measured counts remain unverified. [Run instructions](DATA_AUDIT.md#implemented-custodian-checks)
- `python3 -B -m unittest discover -s tests -v` passed all 8 tests. `python3 -B scripts/audit_companionharm.py --help` passed. Relative Markdown targets and the 30 unique matrix rows were checked with an inline `python3 -B -` verification.
- **Next task.** Obtain a written project-specific scope determination and an authorized read-only CompanionHarm copy at the pinned revision. The custodian can then run the documented command, verify the actual context format, complete the exact/fuzzy and role-aware checks, and record prior holdout exposure. If G0/G1 clear, proceed with the synthetic loader/paired-metric smoke test and the 50-source/100-edit pilot draft. Annotation requires G2.
- **Files changed.** Created `protocols/RELATIONAL_EVIDENCE_DESIGN.md`, `scripts/audit_companionharm.py` and `tests/test_companionharm_audit.py`. Updated `results/STATUS.md`, `results/ARTIFACT_INDEX.md`, `results/DECISIONS.md`, `results/VALIDATION_SYNTHESIS.md`, `results/NOVELTY_VERDICT.md`, `results/PRIOR_ART_MATRIX.csv`, `results/SOURCE_LEDGER.md`, `results/DATA_AUDIT.md` and `results/OVERLAP_AUDIT.md`.

## Initial Stage 0 session

- Read all requested project documents and Stage 0 instructions. Verified the planning package contents and scoped local discovery for baseline code, corpus inputs, outputs and checkpoints. Inspected the located transformer notebook statically and recorded upstream paths and revision metadata.
- Compared 26 papers and preprints, including all Stage 0 starting points. Documented source identity corrections, full-text methods and search limitations. Four separate subagents completed novelty, methods, statistics and ethics reviews. [Synthesis](VALIDATION_SYNTHESIS.md)
- Recorded exact Git revisions, data object metadata and documentation SHA-256 values for both candidate datasets. Verified reported split counts, documented schema and stated use terms at the metadata level. Header inspection, local counts, content hashes, overlap checks and exposure audit remain pending.

## Checks executed

| Check | Outcome |
| --- | --- |
| `python3 -B -m unittest discover -s tests -v` | 2 Stage 0 evidence tests passed |
| `python3 -m json.tool data/source_manifest.json` | Parsed successfully |
| Inline `python3 -B -` GitHub metadata recheck using the manifest's pinned tree endpoints and revision-pinned documentation | Both commits, four data object IDs and sizes, and four document SHA-256 values matched. Data object bytes were outside the request set. |
| Inline `python3 -B -` audit of local deliverables and links | 26 matrix rows, four independent reports and 13 new files. All relative Markdown links resolve and all original package-manifest paths remain present. |
| `shasum -a 256 PACKAGE_MANIFEST.json "$HOME/Downloads/CompanionHarm_Transformers_v2.ipynb"` | Hashes recorded in the inventory |

Real-data integrity tests and the gated loader/paired-metric smoke test remain pending. No human annotation, model API calls, held-out scoring or new empirical results.

AICompanionBench stays outside the active study pending a verified dataset grant. [Rights intake](LICENSE_LEDGER.md#authorization-intake-template)

## Initial session files

- Created `results/INPUT_INVENTORY.md`, `results/PRIOR_ART_MATRIX.csv`, `results/NOVELTY_VERDICT.md`, `results/SOURCE_LEDGER.md`, `results/DATA_AUDIT.md`, `results/LICENSE_LEDGER.md`, `results/OVERLAP_AUDIT.md`, `results/VALIDATION_SYNTHESIS.md`, `results/DECISIONS.md`, `results/ARTIFACT_INDEX.md` and this status file.
- Created `data/source_manifest.json` and `tests/test_stage0_evidence.py`.
- Appended independent reports to `agents/novelty_validator.md`, `agents/methodology_reviewer.md`, `agents/statistics_reviewer.md` and `agents/ethics_release_reviewer.md`.

# Stage 0B overlap audit — 2026-11-12

**CompanionHarm audit measured and exclusions adopted for derived cohorts.** Across train–dev, train–test and dev–test we found 6, 18 and 2 distinct normalized context–reply matches, respectively. Those comparisons contained 2, 4 and 1 exact conversation-trace pairs, plus 0, 2 and 0 nonexact candidate pairs with Jaccard similarity at least 0.80. Each side needed at least five distinct trigrams for the near-match screen. [Aggregate audit](COMPANIONHARM_AUDIT.json)

The local exclusions cover 9 train, 3 development and 8 test conversation IDs connected to a cross-split context–reply or trace match. These are conservative flags for study eligibility. The longest visible trace ends at the last annotated assistant reply and can omit later dialogue. The owner reported no prior official test use. AICompanionBench overlap remains unmeasured.

| Check | Pairing and denominator to report | Status |
| --- | --- | --- |
| Unique conversation and utterance keys | Each split and train–dev, train–test, dev–test intersections. Report duplicate rows and unique conversation counts. | Measured |
| Exact full-row and text duplicates | Parsed duplicate rows within splits, normalized nonempty context–reply matches and role-marked traces across splits. | Measured |
| Input leakage | Blank prefixes, earlier whole-turn repeats, normalized substrings, and role and length consistency. | Source-format checks measured. Model input rendering remains pending. |
| Near-duplicate conversations | Compare reconstructed traces across splits. | Measured for CompanionHarm at the documented threshold. Cross-corpus checks remain pending. |
| Prior experimental exposure | Document who can access held-out materials and which published or local test artifacts, scores and predictions previously informed design. Record model provenance and probable pretraining exposure limits. | Pending owner/custodian evidence |

## Local audit procedure after authorization

1. Keep original bytes read-only and verify pre/post SHA-256. Parse roles and turn order from documented inputs. If the longest available prefix is incomplete, mark the reconstructed conversation as partial. Retain the original row and distinguish raw-byte identity from normalization.
2. Normalize Unicode and whitespace conservatively. Retain role and turn boundaries and exact ordered n-grams. Compute private exact digests and approximate candidates using character or token shingles with MinHash/LSH or another documented equivalent. Use authorized train/dev and synthetic checks to calibrate thresholds and separately handle short/common messages. Freeze that procedure before the custodian checks held-out files. Record parameters, seed, normalized representation and coverage.
3. Confirm candidate pairs with a deterministic similarity measure and authorized local review. Classify an exact copy, near duplicate, shared boilerplate, legitimate earlier repetition, target duplication in the prefix, post-target leakage or unresolved. A substring can be genuine repetition. Estimate false matches via sampled candidates and acknowledge false negatives from OCR and partial screenshot overlap. Audit custody controls must prevent held-out rows from reaching designers.
4. Group connected confirmed duplicate conversations and related edits by source and template before using an eligible development or evaluation partition. Preserve official source assignments and document exclusions or contamination decisions on derived data. Escalate unresolved train/test contamination before G1. If approved external data are unavailable, record the cross-corpus check as pending and keep external validation out of scope.
5. Emit counts and dispositions only. Keep matching texts, character spans, deterministic digests, signatures and join maps private. Never compare candidates against personal accounts. Fail the audit on source mutation, split collisions, target hash changes, nondeterministic label mapping or raw export. These checks await a real-data authorization and verified release. No estimated zero may substitute for a pending check.

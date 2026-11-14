# Stage 8 — manuscript, review, and submission

Paper should target NLP evaluation venues (e.g. ACL/EMNLP Findings, after checking current calls). Do not guarantee acceptance. Create a complete draft with `TBD` placeholders for unavailable empirical content, **never made-up numbers**.

Proposed outline:
1. Abstract (write final after results)
2. Introduction — justified context sensitivity in companion harm *detection*
3. Related work — CompanionHarm, AICompanionBench, CompanionSafe, ConCI, context-flip safety, toxicity context sensitivity, evidence faithfulness, human labeling
4. Task and benchmark construction — fixed target, paired contexts, human validated relation, exclusions
5. Baselines and interventions
6. Primary results — UFR, CCAR, paired joint accuracy, uncertainty
7. Diagnostic analysis — what context changed, qualitative synthetic illustrative cases
8. Optional routing and external data (only if completed)
9. Limitations and ethics — no causal claim of real-world psychological harm, constructed edits, Replika source, annotation and licenses
10. Conclusion

Required deliverables `paper/main.tex`, `paper/references.bib`, `results/CLAIM_EVIDENCE_LEDGER.csv`, `results/REPRODUCIBILITY_CHECKLIST.md`, `results/REVIEWER_OBJECTIONS.md`. Figures must be reproducible from recorded run IDs; every substantive empirical assertion points to a result artifact. Clearly distinguish original CompanionHarm published numbers and reproduced numbers.

Adversarial reviews: novelty validator, methodology reviewer, statistical reviewer, ethics/release reviewer. Address each blocker in a response-to-reviewers document; unresolved material issues appear prominently in limitations or stop submission. Check target venue author guidelines, anonymization, source/data permissions, and citation metadata immediately before submitting.

# Pilot feasibility report

**Status on 2026-11-13: candidate preparation.** The queue contains 50 development source replies from distinct conversations and 100 intended edit slots. It contains no accepted edits or independent ratings. The probability and enriched strata contain 25 sources each. [Queue manifest](PILOT_QUEUE.json)

## Local candidate drafting

The boundary drafting pass used a pinned 4-bit Qwen3-1.7B checkpoint locally, with one bounded generation per source and no dialogue transfer. It processed all 50 sources and produced one structurally usable edit suggestion. Forty-one sources yielded no usable draft and eight outputs failed parsing. These are drafting-model outcomes. They do not estimate the human constructibility, coherence, label relation, or benchmark yield. [Boundary drafting aggregate](PILOT_DRAFTING.json)

A second bounded pass used the broader fiction, boundary and vulnerability prompt on the same 50 sources. It yielded ten structurally usable suggestions: seven fiction-frame changes, one vulnerability change, and two distractor edits. The two runs were retained separately. Both sets of suggestions are attached to `private_data/boundary_pilot/review_drafts.jsonl`, with all 50 source decisions and 100 edit slots still pending author review. [Broader drafting aggregate](PILOT_DRAFTING_BROAD.json)

## Human review and feasibility decision

The author needs to inspect scope and chronology, retain coherent suggestions, write missing edits where feasible, and record ineligible and unconstructible cases. Use the prepared private `review_drafts.jsonl` file. A separately approved local reviewer process must then obtain blind judgments, lock individual votes, independently adjudicate each condition, and check pair quality. The reply-only diagnostic uses different raters for the same source.

| Outcome | Status |
| --- | --- |
| Screened and accepted sources | Pending human author review |
| Constructed and approved edits | 0 |
| Independent initial ratings | 0 |
| Adjudicated preserving or changing pairs | Pending |
| Agreement, precision and expansion decision | Pending |

The case-level inputs and suggestions are in restricted local storage. The pilot packet defines the approval and assignment prerequisites, rubric, evidence intake and feasibility targets. [Pilot packet](../protocols/BOUNDARY_PILOT_PACKET.md)

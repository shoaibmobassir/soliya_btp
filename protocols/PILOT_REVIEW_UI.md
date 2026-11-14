# Pilot review workspace

Run from the project directory with Python 3.

```bash
python3 -B -m scripts.pilot_review
```

Open <http://127.0.0.1:8765/>. The coordinator can search and select each of the 50 source cases, read the longest released trace and focal reply, screen the source, and record an outcome for each edit. The editor displays AI suggestions under the corresponding edit slot. It saves the same private queue as the terminal editor. Use one editor at a time. Authoring is locked once blinded packets exist.

The [hosted practice site](https://context-evidence-review-practice.aurorahen128.chatgpt.site) opens without an account and uses 18 independently authored eight-message conversations. Progress and any optional nickname stay in the current browser tab. Choose **Restart practice** to clear them. For a local test that exercises assignment and response storage, run `python3 -B -m scripts.pilot_review --demo`, expand **Individual reviewer invitations**, and open a demo link. Local demo data is temporary and isolated from real pilot evidence.

In the reviewer view, each case opens to the conversation and two questions. A single comment box is required for harmful or uncertain answers and optional otherwise. Use **Evidence and certainty** to read each earlier message beside its **Boundary** and **Harm** checkboxes, then record confidence and coherence. Reviewers see all available earlier turns and the focal reply. The coordinator can see the longest released trace, including any available later turns. **Save and continue** records the case and opens the next unfinished one.

## Start an approved round

1. Finish screening and authoring. Confirm eligibility, matching, and clearance of visible identifying content under the plan. Use the exact fixed focal reply throughout.
2. Obtain G2 approval and record it as described in the [pilot packet](BOUNDARY_PILOT_PACKET.md). The approval must cover the corpus, reviewer access route, remote recipients, consent, support, withdrawal, and retention. Prepare blinded packets using the existing command below. The example codes are placeholders for 12 distinct people. Reviewers must be assigned and invited individually.

   ```bash
   python3 -B -m scripts.prepare_blind_pilot \
     --drafts private_data/boundary_pilot/review_drafts.jsonl \
     --reviewers R01 R02 R03 R04 R05 R06 R07 R08 R09 R10 R11 R12 \
     --authorization-ref YOUR_APPROVED_REFERENCE
   ```

3. In the private pilot directory create an owner-only `review_portal.json` using the approved material. The following describes the required fields and is a template.

   ```json
   {
     "authorization_ref": "YOUR_APPROVED_REFERENCE",
     "review_origin": "https://YOUR_APPROVED_REVIEW_HOST",
     "consent": "Approved participant information and consent text",
     "support": "Approved distress, support, skip and withdrawal procedures",
     "allow_reviewer_name": false,
     "categories": {
       "Approved category name": "Approved category definition"
     }
   }
   ```

   Review the [plain-language draft harm guide](../pilot_review/harm_guide.json) against the approved codebook. The guide contains the 13 harmful categories from [CompanionHarm's taxonomy](https://arxiv.org/html/2608.25377v1), adapted for the interface. **No harm** is a separate answer. Include the approved definitions in the portal configuration. Set `allow_reviewer_name` to `true` only if the approved consent and access plan covers collecting optional names or nicknames. Names are visible to the coordinator and kept out of the ratings export.

4. For remote review, connect the approved HTTPS route on an approved network to **only** the reviewer listener at `127.0.0.1:8766`. The route must preserve the configured origin and forward the `Authorization` header. Configure it to avoid logging authorization headers or case content, and apply the approved network access and rate limits. Keep the coordinator port `8765` on loopback. The app does not create a network route. The hosted practice URL cannot connect to the private pilot. A 127.0.0.1 invitation only works on the machine running the app. For an approved in-person local review, use `http://127.0.0.1:8766` in the portal file and omit `--review-origin`.

   ```bash
   python3 -B -m scripts.pilot_review --enable-review --review-origin https://YOUR_APPROVED_REVIEW_HOST
   ```

5. Copy each reviewer’s link from the coordinator dashboard and give it to that assigned reviewer. The link grants access to their assignment without an email address or password. Treat it as a credential. If a link was shared by mistake, replace it in the dashboard. Keep the host awake and the app and approved route running while reviews are open. A submitted or skipped judgment is saved to the private SQLite file on this machine. Reviewers can reopen the same invitation to resume unfinished assignments. The coordinator can refresh to see submission counts.

## Close the round

When every assignment has a response or explicit skip, use **Lock initial ratings** to export `private_data/boundary_pilot/web_evidence/ratings.jsonl` and close reviewer submissions. Use the approved withdrawal process before locking. The app preserves submitted responses and provides the approved support and withdrawal instructions to reviewers.

Use separate, independent reviewers for blinded adjudication and pair quality. Record `adjudication.jsonl` and `quality.jsonl` in the same evidence directory following the pilot packet, with the prescribed access separation. Then choose **Summarize pilot evidence**. The existing validation checks completeness and independence and writes `results/PILOT_HUMAN_AGGREGATE.json`. Review feasibility, both change directions, and expected precision before moving past G3. G4 protocol freeze is required before confirmatory test access.

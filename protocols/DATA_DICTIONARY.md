# Data schema and governance

Do not commit actual raw dialogue in this repository. Example keys are semantic contracts, not a claim about upstream CSV field names.

## Internal sample record (locally encrypted / access-controlled)
- `source_dataset` (`companionharm`/`aicompanionbench`/`synthetic`)
- `source_version_sha256`, `source_conversation_id`, `source_utterance_id`
- `speaker_roles`, `turn_index`, `target_response`, `preceding_context`
- `original_label_14`, `derived_label_binary`, `annotation_votes`, `original_split`
- `target_sha256` and `normalized_context_sha256` 
- `context_available`, `context_overlap_flag`, `redaction_status`, `rights_status`

## Derived edit record
- `pair_id`, `anchor_id`, `variant_id`, `edit_family`, `intended_relation` (`preserve`/`change`/`unknown`), `edit_scope`, `generator_type`, `human_revision`
- `target_sha256` MUST equal anchor across variants.
- `validation_status`, `gold_relation` from independent annotations; keep intended and observed relation separate.
- `source_group_id`, `template_family_id`, `split_id`, `disagreement_distribution`

## Prediction-level metadata for release
- `anonymous_example_id`, `pair_id`, `condition_type`, `model_id`, `seed`, `pred_label`, `pred_prob`, `correct`, `confidence_bin`; no dialogue text, usernames, account names, raw dates, or uniquely identifying snippets.

## Storage
Store raw samples only in ignored `private_data/` with explicit access controls. Public artifacts under `results/public/` must pass a PII/license checker. Provide `data/source_manifest.json` with checksums and URLs but no secret credentials. Never redistribute prohibited source texts or derivative quotations.

# Descriptor JSON V1

Introduce structured JSON decoding for descriptor records while keeping the
current raw-first codec conservative and lossless.

This feature currently covers:
- stable JSON output for known `form` and `module` descriptor records;
- `descriptor_json` blocks in `inspect --json`;
- matching descriptor summaries in `semantic-form`;
- opaque fallback summaries when a descriptor body does not match the known
  `u64-pair-utf16le-v1` layout.

Use this pack when a change touches:
- `src/onec_formbin/container.py`
- `src/onec_formbin/api.py`
- `src/onec_formbin/descriptor_json.py`
- `src/onec_formbin/semantic_form.py`
- CLI, tests, or docs that expose descriptor JSON

Out of scope:
- semantic interpretation of the whole form body;
- assigning business meaning to the two leading `u64` fields without new
  evidence;
- relaxing raw-first repack constraints for unknown records;
- editing holdout fixtures during tuning.

# Inspect Rich JSON V1

Expand the `inspect --json` contract so it becomes a richer machine-readable
view of the parsed container and the top-level backbone of the future
LLM-editable workspace.

This pack is responsible for evolving `inspect --json` toward:
- a stable `container.inspect.json` export;
- richer per-record metadata for codecs, descriptor links, and known record roles;
- container summaries for continuation chains, pointer links, and record layout;
- a machine-readable backbone that downstream semantic export and edit flows can reuse.

Current verified baseline inside this pack:
- stable inspect JSON on the managed fixtures;
- pointer and preserve-policy metadata on the split-form fixture;
- descriptor JSON for known descriptor records via the adjacent descriptor layer.

Use this pack when a change touches:
- `src/onec_formbin/api.py`
- `src/onec_formbin/container.py`
- `src/onec_formbin/cli.py` for `inspect`
- `src/onec_formbin/descriptor_json.py`
- docs or tests that define the inspect JSON contract

Out of scope:
- broadening container support without fixtures;
- semantic parsing of the whole form body;
- semantic edits or rebuild from workspace artifacts;
- editing holdout fixtures during tuning.

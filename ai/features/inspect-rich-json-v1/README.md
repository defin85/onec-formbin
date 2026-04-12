# Inspect Rich JSON V1 Pack

Use this feature pack for the container-backbone layer of the future
LLM-editable form workspace.

Cross-pack source of truth: `docs/workspace-contract.md`.

Current stage:
- `inspect --json` already exposes the stable baseline record list and
  descriptor JSON for known descriptor records;
- the starter manifests keep the current inspect contract green while the
  richer workspace-facing shape is added.

Target outcome:
- evolve `inspect --json` into a stable `container.inspect.json` backbone;
- expose container summaries, record roles, codecs, descriptor links, and
  continuation-chain metadata in one machine-readable place;
- keep existing inspect users stable while workspace-oriented fields are added.

Split intent:
- `dev.jsonl`: baseline inspect guards on normal fixtures while the richer
  workspace backbone grows;
- `holdout.jsonl`: confirmation on the split-form pointer fixture after a
  candidate is kept.

Typical flow:
1. `make validate-feature FEATURE=inspect-rich-json-v1`
2. `make feature-start FEATURE=inspect-rich-json-v1`
3. `make feature-baseline FEATURE=inspect-rich-json-v1 RUN_ID=<run-id>`
4. Add richer `inspect --json` fields in small reversible steps.
5. Replace starter guards with field-specific JSON assertions or goldens as the
   contract hardens.

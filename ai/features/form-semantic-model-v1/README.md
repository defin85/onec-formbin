# Form Semantic Model V1 Pack

Use this feature pack for managed work on the first semantic summary export for
ordinary forms and the future `semantic/` slice layer of the LLM-editable
workspace.

Cross-pack source of truth: `docs/workspace-contract.md`.

Current stage:
- `semantic-form` exports an experimental semantic JSON summary;
- the pack now guards that summary on the verified fixture corpus;
- descriptor summaries already flow through the semantic export.

Target outcome:
- evolve the single summary into stable `semantic/` slices such as
  `form.meta.json`, `events.json`, `commands.json`, `attributes.json`,
  `controls.tree.json`, `layout.json`, and `strings.json`;
- parse a `Form.bin` form payload into a stable semantic workspace export;
- keep split-form continuation handling and raw-first safety intact;
- prepare the base for future semantic diff and semantic edits.

Split intent:
- `dev.jsonl`: baseline semantic-summary checks on normal fixtures and CLI export
  while the `semantic/` slices are introduced;
- `holdout.jsonl`: confirmation on the split-form fixture after a candidate is
  kept.

Typical flow:
1. `make validate-feature FEATURE=form-semantic-model-v1`
2. `make feature-start FEATURE=form-semantic-model-v1`
3. `make feature-baseline FEATURE=form-semantic-model-v1 RUN_ID=<run-id>`
4. Make one small reversible semantic-model change.
5. `make feature-iteration FEATURE=form-semantic-model-v1 RUN_ID=<run-id>`
6. `make feature-holdout FEATURE=form-semantic-model-v1 RUN_ID=<run-id>`

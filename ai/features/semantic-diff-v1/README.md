# Semantic Diff V1 Pack

Use this feature pack for review-oriented semantic diff on top of the future
LLM-editable workspace.

Cross-pack source of truth: `docs/workspace-contract.md`.

Current stage:
- `formbin diff --form-mode semantic` can render the current semantic slices
  for form payload changes;
- the same mode can now diff materialized `semantic/*.json` workspace edits
  between unpack dirs before `apply-semantic`, while still preferring rebuilt
  semantic slices when raw form payloads changed;
- pending `form.meta.json` workspace edits are now guarded explicitly as
  reviewable per-slice hunks before `apply-semantic`;
- pending `controls.tree.json` workspace edits are now guarded explicitly as
  reviewable per-slice hunks before `apply-semantic`, including richer
  control-event binding metadata edits, without leaking derived
  `attributes.json` or `strings.json` before apply;
- pending `attributes.json` workspace edits are now guarded explicitly as
  reviewable per-slice hunks before `apply-semantic`, without leaking derived
  `controls.tree.json` or `strings.json` before apply;
- pending `layout.json` workspace edits are now guarded explicitly as
  reviewable per-slice hunks before `apply-semantic`;
- pending `events.json` workspace edits are now guarded explicitly as
  reviewable per-slice hunks before `apply-semantic`;
- pending `commands.json` workspace edits are now guarded explicitly as
  reviewable per-slice hunks before `apply-semantic`, without leaking derived
  `controls.tree.json` or `strings.json` before apply;
- pending `strings.json` workspace edits are now guarded explicitly as
  reviewable per-slice hunks before `apply-semantic`, including current
  supported alias batches that should not leak derived `form.meta.json`,
  `events.json`, or `commands.json` hunks before apply;
- the manifests keep the current raw and AST diff workflow green alongside the
  new semantic render mode;
- split-form identical-input diff checks stay green in semantic mode.

Target outcome:
- compare forms at a semantic level instead of only raw text or AST JSON;
- diff workspace slices such as `form.meta.json`, `events.json`,
  `commands.json`, `attributes.json`, `controls.tree.json`, and `strings.json`;
- keep current diff behavior available as a fallback;
- prepare review-friendly outputs for future semantic editing flows.

Split intent:
- `dev.jsonl`: baseline raw and AST diff guards on normal fixtures until
  semantic workspace diff artifacts exist;
- `holdout.jsonl`: confirmation on the split-form fixture after a candidate is
  kept.

Typical flow:
1. `make validate-feature FEATURE=semantic-diff-v1`
2. `make feature-start FEATURE=semantic-diff-v1`
3. `make feature-baseline FEATURE=semantic-diff-v1 RUN_ID=<run-id>`
4. Add semantic diff outputs and expected artifacts in small reversible steps.
5. Replace starter guards with semantic diff goldens as the contract hardens.

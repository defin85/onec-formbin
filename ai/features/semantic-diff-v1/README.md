# Semantic Diff V1 Pack

Use this feature pack for review-oriented semantic diff on top of the future
LLM-editable workspace.

Cross-pack source of truth: `docs/workspace-contract.md`.

Current stage:
- roadmap scaffold;
- the starter manifests keep the current raw and AST diff workflow green until
  semantic diff fixtures and expected outputs are added.

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

# Safe Semantic Edits V1 Pack

Use this feature pack for the controlled write path from the future semantic
workspace back to raw editable artifacts.

Cross-pack source of truth: `docs/workspace-contract.md`.

Current stage:
- roadmap scaffold;
- the starter manifests keep current raw-first and AST edit-adjacent paths green
  until semantic edit commands and expected outputs are added.

Target outcome:
- allow a narrow class of semantic edits through `semantic/` slice files;
- rebuild only the affected raw artifacts such as `raw/form.raw` and
  `raw/module.bsl` when that is safe and fixture-backed;
- keep repack safety rules explicit and conservative;
- prepare a path from semantic model to controlled write support.

Split intent:
- `dev.jsonl`: baseline guards on AST build and current edit-adjacent behavior
  while semantic writes are added;
- `holdout.jsonl`: confirmation on preserve-policy and split-form behavior after
  a candidate is kept.

Typical flow:
1. `make validate-feature FEATURE=safe-semantic-edits-v1`
2. `make feature-start FEATURE=safe-semantic-edits-v1`
3. `make feature-baseline FEATURE=safe-semantic-edits-v1 RUN_ID=<run-id>`
4. Add narrow semantic-edit capabilities in small reversible steps.
5. Replace starter guards with semantic-edit fixtures once the edit surface exists.

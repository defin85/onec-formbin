# Form AST Guard Pack

Use this feature pack for managed changes that affect the experimental
`form.raw <-> AST` workflow.

What it protects:
- CLI behavior for `parse-form` and `build-form`;
- AST-backed diff rendering through `formbin diff --form-mode ast`;
- split-form continuation handling for the known fixture set.

Split intent:
- `dev.jsonl`: fast iteration on the baseline AST fixture and AST-mode diff flow;
- `holdout.jsonl`: confirmation on alternate fixtures and split-form behavior.

Typical flow:
1. `make validate-feature FEATURE=form-ast-guard`
2. `make feature-start FEATURE=form-ast-guard`
3. `make feature-baseline FEATURE=form-ast-guard RUN_ID=<run-id>`
4. Make one small reversible AST-related change.
5. `make feature-iteration FEATURE=form-ast-guard RUN_ID=<run-id>`
6. `make feature-holdout FEATURE=form-ast-guard RUN_ID=<run-id>`

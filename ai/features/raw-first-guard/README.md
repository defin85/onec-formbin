# Raw-First Guard Pack

Use this as the default product pack for managed changes to `onec-formbin`.
It maps to the repository's main feature: parsing `Form.bin` through the
raw-first workflow.

What it protects:
- deterministic parsing into the raw-first workspace;
- end-to-end CLI behavior for `inspect`, `unpack`, `pack`, `roundtrip-check`,
  `diff`, and the experimental form AST entrypoints;
- mirror versus preserve size-policy behavior on the verified corpus.

Split intent:
- `dev.jsonl`: fast feedback on baseline fixtures that represent the normal path;
- `holdout.jsonl`: confirmation on the split-form preserve-policy fixture after a
  candidate is kept.

Typical flow:
1. `make validate-feature FEATURE=raw-first-guard`
2. `make feature-start FEATURE=raw-first-guard`
3. `make feature-baseline FEATURE=raw-first-guard RUN_ID=<run-id>`
4. Make one small reversible change.
5. `make feature-iteration FEATURE=raw-first-guard RUN_ID=<run-id>`
6. `make feature-holdout FEATURE=raw-first-guard RUN_ID=<run-id>`

Use a narrower pack such as `container-core-guard` or `form-ast-guard` only when
the change stays inside that slice and you want tighter, faster metrics.

Local fixtures for initial codec verification.

The current verified support matrix is intentionally limited to the three
fixtures below. `README.md` and `docs/verification.md` mirror this same matrix
at a higher level.

## Fixture matrix

- `common-indicator.Form.bin`
  - baseline inspect/unpack/pack/round-trip coverage
  - `container.inspect.json` export baseline coverage
  - standard module + form payload handling
  - descriptor JSON baseline coverage
  - workspace descriptor artifact baseline coverage
- `common-print-form.Form.bin`
  - mirror-record size-changing module edits
  - mirror-record size-changing form edits
  - raw diff and AST-rendered form diff coverage
  - AST canonical build fixed-point coverage
  - semantic-slice workspace materialization coverage
  - support-artifact workspace materialization coverage
  - safe semantic edit baseline coverage for form title, event handler, command name/title, control name, control-pattern attribute name/data_path, and supported string aliases
  - AST JSON round-trip coverage
  - descriptor JSON and semantic-model descriptor coverage
- `i584-load-form.Form.bin`
  - non-mirror record size-preservation enforcement
  - split-form continuation handling
  - `container.inspect.json` holdout export coverage
  - opaque trailing record coverage
  - descriptor JSON holdout coverage
  - workspace descriptor artifact holdout coverage
  - split-form semantic export holdout coverage
  - split-form support-artifact export holdout coverage
  - split-form `apply-semantic` rejection coverage

## Non-claims

These fixtures do not prove:

- full semantic parsing of ordinary forms
- support for every undocumented header variant
- byte-identical formatting reconstruction from AST output

Before publishing the repository, replace these files with sanitized samples.

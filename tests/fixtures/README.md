Local fixtures for initial codec verification.

## Fixture matrix

- `common-indicator.Form.bin`
  - baseline inspect/unpack/pack/round-trip coverage
  - standard module + form payload handling
- `common-print-form.Form.bin`
  - mirror-record size-changing module edits
  - raw diff and AST-rendered form diff coverage
  - AST JSON round-trip coverage
- `i584-load-form.Form.bin`
  - non-mirror record size-preservation enforcement
  - split-form continuation handling
  - opaque trailing record coverage

## Non-claims

These fixtures do not prove:

- full semantic parsing of ordinary forms
- support for every undocumented header variant
- byte-identical formatting reconstruction from AST output

Before publishing the repository, replace these files with sanitized samples.

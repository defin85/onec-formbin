# Repository Map

This repository is intentionally small. Use this document as the primary map
before reading code file-by-file.

## Top-level layout

- `src/onec_formbin/`: package source
- `tests/`: fixture-backed behavior tests
- `tests/fixtures/`: local `Form.bin` samples and support matrix
- `docs/adr/0001-raw-first.md`: accepted raw-first architecture decision

## Main code paths

### CLI entry points

- `src/onec_formbin/cli.py`
- Commands:
  - `inspect`
  - `unpack`
  - `pack`
  - `roundtrip-check`
  - `diff`
  - `parse-form`
  - `build-form`

Edit this file when the command surface, options, exit codes, or user-visible
messages change.

### Raw-first container workflow

- `src/onec_formbin/api.py`
- `src/onec_formbin/container.py`
- `src/onec_formbin/workspace.py`
- `src/onec_formbin/models.py`

Responsibilities:

- parse container bytes into records
- classify records conservatively
- unpack records into a manifest + `records/` tree
- repack while preserving unknown bytes and refusing unsafe size changes

Edit these files for container structure, manifest schema, record naming,
pointer handling, and repack safety policy.

### Diff workflow

- `src/onec_formbin/diffing.py`

Responsibilities:

- load either packed files or unpack directories
- compare metadata and payload bytes
- render raw or AST-backed text diffs

Edit this file when diff behavior, reporting, or form render modes change.

### Experimental AST workflow

- `src/onec_formbin/form_ast.py`

Responsibilities:

- parse `form.raw` brace syntax into a generic AST
- serialize AST back into brace text
- support split-form continuation records for known fixtures

This layer is intentionally separate from the main pack/unpack codec. Do not
make raw container safety depend on AST semantics.

## Change guidance

- If a change affects record parsing or repack policy, verify round-trip and
  size-policy behavior first.
- If a change affects CLI output or exits, verify the CLI directly in addition
  to running tests.
- If a change broadens support claims, update `README.md` and
  `tests/fixtures/README.md` together.

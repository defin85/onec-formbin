# onec-formbin

Standalone tool for inspecting, unpacking, and repacking 1C ordinary-form
`Form.bin` containers.

Current focus:
- deterministic container scanning
- lossless unpack/pack
- conservative text editing support for known UTF-8 payload records
- container-aware diff
- experimental `form.raw <-> AST` conversion

Non-goals for the first version:
- full semantic parsing of ordinary forms
- guaranteed support for every unknown header variant
- automatic rebuilding of all undocumented size fields

## Why this repo exists

`Form.bin` files are not plain brace files. In the local corpus they contain a
stable container prefix, multiple record headers, UTF-16LE-named descriptors,
UTF-8 text payloads, and opaque trailing chunks. Existing tools such as
`v8unpack` are useful as prior art, but they do not provide a ready-made,
standalone `Form.bin` unpack/pack workflow.

This repo therefore starts with a raw-first codec:
- parse the outer container
- expose every record as an editable artifact
- preserve unknown bytes
- repack conservatively

## Install

```bash
uv sync
```

Requires Python 3.12+.

## Project docs

- `docs/repo-map.md`: module map and change guidance
- `docs/verification.md`: bootstrap, smoke, and full verification commands
- `docs/agent/index.md`: repo-local router for the eval-driven process layer
- `tests/fixtures/README.md`: fixture matrix and verified support boundaries
- `docs/adr/0001-raw-first.md`: raw-first architecture decision

## Agent workflow

```bash
make codex-onboard
make agent-verify
make validate-feature FEATURE=raw-first-guard
```

For eval-driven feature work, use the feature packs under `ai/features/` together
with the loop commands from `Makefile`.

## CLI

```bash
uv run formbin inspect tests/fixtures/common-indicator.Form.bin
uv run formbin unpack tests/fixtures/common-indicator.Form.bin -o /tmp/formbin-unpack
uv run formbin pack /tmp/formbin-unpack -o /tmp/common-indicator.repacked.Form.bin
uv run formbin roundtrip-check tests/fixtures/common-indicator.Form.bin
uv run formbin diff a.Form.bin b.Form.bin
uv run formbin diff /tmp/unpack-a /tmp/unpack-b --form-mode ast
uv run formbin parse-form /tmp/formbin-unpack/records/004-form.raw -o /tmp/form.ast.json
uv run formbin build-form /tmp/form.ast.json -o /tmp/form.raw
```

## Unpack layout

```text
out/
├── manifest.json
├── prefix.bin
└── records/
    ├── 000-opaque.bin
    ├── 001-form.descriptor.bin
    ├── 002-form.raw
    ├── 003-module.descriptor.bin
    └── 004-module.bsl
```

Rules:
- every container record is preserved
- UTF-8 BOM text payloads are written without BOM for editing
- binary records remain raw `.bin`
- `manifest.json` records header fields, codec, hashes, and safe repack policy

## Repack policy

The tool supports three practical cases:
- exact no-op repack
- size-changing edits for records where `field1 == field2`
- size-preserving edits for records with undocumented non-mirrored header fields

If a record has undocumented size semantics, the tool refuses unsafe
size-changing edits instead of emitting a likely-broken file.

## Diff

`formbin diff` compares either:
- two `Form.bin` files
- two unpack directories produced by `formbin unpack`

It reports:
- prefix changes
- added or removed records
- metadata changes per record
- unified text diff for `module` and `form` payloads

For form payloads you can choose:
- `--form-mode raw`: diff raw brace text
- `--form-mode ast`: diff experimental AST JSON rendering

The command exits with code `0` for identical inputs and `1` for differences.

## Experimental AST layer

`parse-form` and `build-form` are intentionally separate from the main
unpack/pack path.

They parse `form.raw` into a generic brace AST:
- list nodes
- atom nodes
- literal nodes for braced `#base64` blocks
- string nodes

Current guarantees:
- parser/serializer round-trips through the AST structure
- the main `Form.bin` codec does not depend on the experimental layer

Current non-guarantees:
- semantic understanding of ordinary-form concepts
- byte-identical reconstruction of the original `form.raw` formatting
- safety of using AST-built output for every undocumented container variant

For pointer-split forms where the `form` record continues in a later opaque
record, run `parse-form` against the source `Form.bin` or the unpack root
directory. A standalone `records/*-form.raw` file may be incomplete by design.

## Status

Verified locally against three fixtures:
- a small form with module + form records
- a larger form with module + form records
- a form with non-standard header fields and an opaque trailing record

Before publishing this repo, sanitize or replace local fixtures if they contain
project-specific code.

## Development

```bash
uv sync
uv run formbin inspect tests/fixtures/common-indicator.Form.bin
uv run ruff check .
uv run pytest
```

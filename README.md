# onec-formbin

Standalone tool for inspecting, unpacking, and repacking 1C ordinary-form
`Form.bin` containers.

Current focus:
- deterministic container scanning
- lossless unpack/pack
- conservative text editing support for known UTF-8 payload records
- descriptor JSON visibility and workspace artifacts for known descriptor records
- container-aware diff
- experimental `form.raw <-> AST` conversion
- experimental semantic-form summary export

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
- `docs/workspace-contract.md`: source of truth for the future LLM-editable workspace
- `docs/agent/index.md`: repo-local router for the eval-driven process layer
- `tests/fixtures/README.md`: fixture matrix and verified support boundaries
- `docs/adr/0001-raw-first.md`: raw-first architecture decision

## Verified fixture matrix

Current verified variants in the local corpus are:

- `common-indicator.Form.bin`: baseline module + form fixture for inspect,
  unpack/pack, and byte-identical roundtrip.
- `common-print-form.Form.bin`: mirror-policy fixture for diff, semantic
  export, and current verified size-changing `module` and `form` payload edits.
- `i584-load-form.Form.bin`: split-form preserve-policy fixture for
  continuation handling and explicit refusal of unsupported size-changing
  repack edits.

## Agent workflow

```bash
make codex-onboard
make agent-verify
make feature-resume FEATURE=raw-first-guard
make validate-feature FEATURE=raw-first-guard
make validate-feature FEATURE=container-core-guard
make validate-feature FEATURE=form-ast-guard
```

For eval-driven feature work, start with `raw-first-guard` for the repository's
main feature, parsing `Form.bin` through the raw-first workflow. On a new
session, run `make feature-resume FEATURE=raw-first-guard` first and continue
the reported `RUN_ID` when one already exists. `make feature-start` now refuses
to create a duplicate run when `feature-resume` already finds one. Switch to the
narrower feature packs only when the change clearly stays inside that slice.

## CLI

```bash
uv run formbin inspect tests/fixtures/common-indicator.Form.bin
uv run formbin unpack tests/fixtures/common-indicator.Form.bin -o /tmp/formbin-unpack
uv run formbin inspect /tmp/formbin-unpack --json
uv run formbin pack /tmp/formbin-unpack -o /tmp/common-indicator.repacked.Form.bin
uv run formbin roundtrip-check tests/fixtures/common-indicator.Form.bin
uv run formbin diff a.Form.bin b.Form.bin
uv run formbin diff /tmp/unpack-a /tmp/unpack-b --form-mode ast
uv run formbin diff /tmp/unpack-a /tmp/unpack-b --form-mode semantic
uv run formbin parse-form /tmp/formbin-unpack/records/004-form.raw -o /tmp/form.ast.json
uv run formbin build-form /tmp/form.ast.json -o /tmp/form.raw
uv run formbin semantic-form tests/fixtures/common-print-form.Form.bin -o /tmp/form.semantic.json
uv run formbin apply-semantic /tmp/formbin-unpack
```

## Unpack layout

```text
out/
├── container.inspect.json
├── descriptors/
│   ├── form.descriptor.json
│   └── module.descriptor.json
├── manifest.json
├── prefix.bin
├── semantic/
│   ├── form.meta.json
│   ├── events.json
│   ├── commands.json
│   ├── attributes.json
│   ├── controls.tree.json
│   ├── layout.json
│   └── strings.json
└── records/
    ├── 000-opaque.bin
    ├── 001-form.descriptor.bin
    ├── 002-form.raw
    ├── 003-module.descriptor.bin
    └── 004-module.bsl
```

Rules:
- `container.inspect.json` mirrors the current `inspect --json` backbone for workspace tooling
- `descriptors/*.descriptor.json` mirrors the current structured summary for known descriptor records
- `semantic/*.json` mirrors the current experimental semantic workspace slices
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

Current verified mirror-safe size-changing cases on
`common-print-form.Form.bin` include both `module` and `form` payload edits.

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
- `--form-mode semantic`: diff the current semantic slice JSON export with
  per-slice hunks

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
- on `common-print-form.Form.bin`, one rebuilt `form.raw` stays stable on the
  second parse/build cycle
- the main `Form.bin` codec does not depend on the experimental layer

Current non-guarantees:
- semantic understanding of ordinary-form concepts
- byte-identical reconstruction of the original `form.raw` formatting
- safety of using AST-built output for every undocumented container variant

For pointer-split forms where the `form` record continues in a later opaque
record, run `parse-form` against the source `Form.bin` or the unpack root
directory. A standalone `records/*-form.raw` file may be incomplete by design.

## Experimental semantic model layer

`semantic-form` builds an experimental semantic JSON summary from a `Form.bin`,
an unpack root directory, or a standalone `form.raw` file.

Current guarantees:
- exposes container-level form and module metadata when the source has it;
- carries the current inspect/container backbone as `container.inspect_backbone`
  when available;
- carries bridge semantic slices as `semantic["form.meta.json"]`,
  `semantic["events.json"]`, `semantic["commands.json"]`,
  `semantic["attributes.json"]`, `semantic["controls.tree.json"]`,
  `semantic["layout.json"]`, and `semantic["strings.json"]`;
- carries descriptor JSON summaries for known `form` and `module` descriptors;
- reports AST-derived structure counts, top-level shape, and string samples;
- works with split-form continuation on the verified fixture corpus.

Current non-guarantees:
- full ordinary-form semantics;
- semantic meaning of the leading descriptor integers;
- full attribute semantics beyond the current control-pattern bridge;
- full control-event coverage or stable non-form event ownership;
- full command ownership or action-only command coverage;
- layout visibility semantics beyond the current coarse bridge;
- stable field names for every future semantic expansion;
- editing every semantic slice back into `form.raw`.

## Experimental semantic edits

`apply-semantic` applies the current opt-in writable subset from an unpacked
semantic workspace back into `records/*-form.raw` and then refreshes the
materialized `semantic/*.json` slices.

Current guarantees:
- works on the verified non-split unpack fixture path;
- supports `semantic/form.meta.json.form_title`;
- supports `semantic/events.json[].handler` for the current form-scope bridge;
- supports `semantic/commands.json[].name/title` for the current command bridge;
- supports direct `semantic/controls.tree.json[].name/title` edits for current
  explicit non-root control bridge items;
- supports direct `semantic/attributes.json[].name/data_path` edits for current
  explicit control-pattern bridge items when both fields stay in sync;
- supports `semantic/strings.json[].value` only when it aliases one of those
  already-supported write paths, including current command `name/title` aliases,
  or the current explicit `control_name` bridge items.

Current non-guarantees:
- writes to split-form unpack workspaces;
- writes to unsupported `attributes.json` fields, structural
  `controls.tree.json` fields, or `layout.json`;
- arbitrary `strings.json` edits outside the supported alias roles.

## Experimental inspect JSON backbone

`inspect --json` now exposes additive machine-readable workspace metadata on
top of the stable record list, and `unpack` writes the same shape to
`container.inspect.json`.

The `inspect` command can read either a source `Form.bin` file or an unpack
directory that already contains `container.inspect.json`.

Current guarantees:
- every record exposes `codec`, `record_role`, and `workspace_relative_path`;
- known `form` and `module` payload records expose `linked_descriptor_index`;
- records that participate in split payloads expose `continuation_chain`;
- the top-level output summarizes descriptor/payload links and continuation
  chains through `descriptor_links` and `continuation_chains`;
- the top-level output summarizes pointer targets and byte layout through
  `pointer_links` and `record_layout`.

Current non-guarantees:
- that every future container role is already classified semantically;
- that these additive fields replace the raw-first unpack manifest;
- stability of any semantic layer beyond the documented machine-readable
  inspect backbone.

## Experimental descriptor JSON

`inspect --json` now includes `descriptor_json` for known `form` and `module`
descriptor records, and `unpack` writes the same summaries to
`descriptors/form.descriptor.json` and `descriptors/module.descriptor.json`.

Current guarantees:
- known descriptor bodies are decoded as the observed `u64-pair-utf16le-v1`
  shape;
- unpack materializes the current descriptor summary shape as workspace artifacts
  for known `form` and `module` descriptors;
- unknown descriptor bodies fall back to opaque summaries without changing the
  raw-first unpack/pack path.

Current non-guarantees:
- semantic meaning of the leading `u64` values;
- support for every future descriptor-body layout.

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

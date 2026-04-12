# Workspace Contract

This document is the source of truth for the future LLM-editable workspace for
ordinary-form `Form.bin` inputs.

It defines:
- canonical artifact names;
- pack ownership boundaries;
- minimum schema expectations;
- the current status of each artifact.

It does not claim that every artifact already exists today.

## Status Terms

- `current`: exported by the repository today.
- `bridge`: current precursor that exists today, but is expected to evolve into
  the target artifact.
- `planned`: target artifact name and contract are fixed here, but the export is
  not implemented yet.

## Global Rules

- Text artifacts use UTF-8. JSON artifacts use two-space indentation and end
  with a trailing newline.
- JSON output must be deterministic: stable field names, stable item ordering,
  and no timestamp noise inside the artifact body.
- Unknown or unsupported bytes must remain represented in the raw/container
  layers. Semantic layers must not silently discard them.
- The raw-first unpack/pack workflow remains the safety boundary for rebuilds.
- Semantic layers are additive. They summarize or normalize known structure, but
  they do not replace the raw artifacts.
- Semantic write support is opt-in and owned only by `safe-semantic-edits-v1`.
  All semantic artifacts are read-only by default.
- If a pack changes a canonical artifact name or meaning, update this document
  in the same change.

## Canonical Layout

```text
form-workspace/
├── manifest.json
├── container.inspect.json
├── descriptors/
│   ├── form.descriptor.json
│   └── module.descriptor.json
├── raw/
│   ├── form.raw
│   └── module.bsl
├── ast/
│   └── form.ast.json
└── semantic/
    ├── form.meta.json
    ├── events.json
    ├── commands.json
    ├── attributes.json
    ├── controls.tree.json
    ├── layout.json
    └── strings.json
```

## Root And Raw Artifacts

### `manifest.json`

- Status: `current`
- Primary owner: `raw-first-guard`, `container-core-guard`
- Current source: `formbin unpack`
- Contract:
  - keep the existing unpack-manifest schema as the raw-first source of truth;
  - do not silently repurpose this file into a semantic artifact;
  - future workspace exports may copy or extend this manifest, but only in an
    additive way.

### `raw/form.raw`

- Status: `current`
- Primary owner: `raw-first-guard`, `form-ast-guard`
- Current source: unpacked form record or rebuilt AST output
- Contract:
  - stores the editable brace-text payload for the known form record;
  - may be incomplete when the source form uses continuation records and the
    export was taken from a standalone raw file instead of a full container.

### `raw/module.bsl`

- Status: `current`
- Primary owner: `raw-first-guard`
- Current source: unpacked module record
- Contract:
  - stores the editable BSL module text when the source contains a module record;
  - remains the canonical raw module artifact even if semantic slices are added.

### `ast/form.ast.json`

- Status: `current`
- Primary owner: `form-ast-guard`
- Current source: `formbin parse-form`
- Contract:
  - stores the generic brace AST bridge format for `form.raw`;
  - stays explicitly lower-level than semantic slices;
  - remains a bridge artifact, not the final semantic workspace format.

## Container Backbone

### `container.inspect.json`

- Status: `bridge`
- Primary owner: `inspect-rich-json-v1`
- Current precursor: `formbin inspect --json`
- Contract:
  - top-level object;
  - required baseline keys:
    - `path`
    - `prefix_sha256`
    - `record_count`
    - `records`
  - each record object must keep the current baseline keys:
    - `index`
    - `header_start`
    - `body_start`
    - `body_end`
    - `field1`
    - `field2`
    - `field3`
    - `kind`
    - `label`
    - `size_policy`
    - `pointer_record_index`
    - `body_sha256`
  - known descriptor records may add `descriptor_json`;
  - future fields must be additive and machine-readable, for example:
    - `codec`
    - `record_role`
    - `continuation_chain`
    - `linked_descriptor_index`
    - `workspace_relative_path`

### `descriptors/form.descriptor.json`

- Status: `planned`
- Primary owner: `descriptor-json-v1`, consumed by `inspect-rich-json-v1`
- Current precursor: `descriptor_json` inside `inspect --json` and `semantic-form`
- Contract:
  - top-level object;
  - required keys:
    - `format`
    - `body_size`
  - for known `u64-pair-utf16le-v1` descriptors, required additive keys:
    - `field_a_u64_le`
    - `field_b_u64_le`
    - `u64_values_match`
    - `leading_nul_u16_count`
    - `name_utf16le`
    - `trailing_nul_u16_count`
    - `name_matches_record_label`
  - for unknown descriptor layouts, fallback keys:
    - `format = "opaque"`
    - `body_sha256`
    - `hex_preview`

### `descriptors/module.descriptor.json`

- Status: `planned`
- Primary owner: `descriptor-json-v1`, consumed by `inspect-rich-json-v1`
- Contract:
  - same shape rules as `descriptors/form.descriptor.json`;
  - the artifact name is fixed even when the module record is absent, but the
    file itself is only exported when a module descriptor exists.

## Semantic Slice Artifacts

All semantic slice files are owned by `form-semantic-model-v1` for read/export,
extended by `safe-semantic-edits-v1` for controlled writes, and consumed by
`semantic-diff-v1` for review/diff output.

### Common Semantic Rules

- Every `semantic/*.json` artifact is a top-level object.
- Every artifact must contain:
  - `schema`
  - `version`
- The `schema` value must be file-specific and stable.
- Item arrays inside semantic slices must be deterministic.
- IDs inside semantic slices must be stable within a single export/import
  roundtrip on the same tool version. Cross-version stability is not yet
  promised unless fixture-backed.

### `semantic/form.meta.json`

- Status: `planned`
- Schema: `onec-formbin.form-meta.v1`
- Contract:
  - required keys:
    - `schema`
    - `version`
    - `form_name`
    - `form_title`
    - `form_kind`
    - `root_item_id`
    - `flags`
  - `flags` is an object of normalized top-level booleans or enums;
  - this file owns top-level form properties only and must not duplicate the
    full control tree.

### `semantic/events.json`

- Status: `planned`
- Schema: `onec-formbin.events.v1`
- Contract:
  - required keys:
    - `schema`
    - `version`
    - `items`
  - `items` is an array of objects with:
    - `name`
    - `handler`
    - `scope`
    - `owner_id`

### `semantic/commands.json`

- Status: `planned`
- Schema: `onec-formbin.commands.v1`
- Contract:
  - required keys:
    - `schema`
    - `version`
    - `items`
  - `items` is an array of objects with:
    - `id`
    - `name`
    - `title`
    - `owner_id`
    - `source`

### `semantic/attributes.json`

- Status: `planned`
- Schema: `onec-formbin.attributes.v1`
- Contract:
  - required keys:
    - `schema`
    - `version`
    - `items`
  - `items` is an array of objects with:
    - `id`
    - `name`
    - `data_path`
    - `type_hint`
    - `role`

### `semantic/controls.tree.json`

- Status: `planned`
- Schema: `onec-formbin.controls-tree.v1`
- Contract:
  - required keys:
    - `schema`
    - `version`
    - `root_id`
    - `items`
  - `items` is an array of nodes with:
    - `id`
    - `kind`
    - `name`
    - `title`
    - `parent_id`
    - `child_ids`
  - this file owns structure, parent/child hierarchy, and stable node ordering.

### `semantic/layout.json`

- Status: `planned`
- Schema: `onec-formbin.layout.v1`
- Contract:
  - required keys:
    - `schema`
    - `version`
    - `items`
  - `items` is an array of objects with:
    - `control_id`
    - `container_id`
    - `order`
    - `group_kind`
    - `visibility`

### `semantic/strings.json`

- Status: `planned`
- Schema: `onec-formbin.strings.v1`
- Contract:
  - required keys:
    - `schema`
    - `version`
    - `items`
  - `items` is an array of objects with:
    - `id`
    - `value`
    - `owner_kind`
    - `owner_id`
    - `role`

## Initial Write Budget

The default mode is read-only. When `safe-semantic-edits-v1` begins exposing
write support, the intended initial writable subset is:

- `semantic/form.meta.json`
  - display-oriented top-level properties only
- `semantic/events.json`
  - handler names only
- `semantic/commands.json`
  - command titles only
- `semantic/controls.tree.json`
  - selected labels, visibility flags, and child order in known containers
- `semantic/strings.json`
  - string values

Everything else stays read-only until fixture-backed evidence justifies it.

## Diff Contract

`semantic-diff-v1` should consume the canonical semantic slice paths from this
document.

The target semantic diff output must:
- stay deterministic;
- preserve the current raw and AST diff modes as fallbacks;
- report changes per semantic slice instead of flattening everything into one
  prose-only blob.

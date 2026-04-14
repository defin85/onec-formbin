# Workspace Contract

This document is the source of truth for the LLM-editable workspace and public
versioned bundle contract for ordinary-form `Form.bin` inputs.

It defines:
- canonical artifact names;
- pack ownership boundaries;
- minimum schema expectations;
- the public external bundle name and version boundary;
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
- Cross-repo consumers must bind only to the documented bundle contract and
  file-level schemas in this document, not to internal Python objects or ad hoc
  AST traversal details.
- If a pack changes a canonical artifact name or meaning, update this document
  in the same change.

## Public External Bundle Contract

- Public bundle id: `ordinary-form-bundle.v1`
- Primary owner: `ordinary-form-bundle-v1`
- Intended use:
  - agent-readable export/edit/apply/pack workspace for ordinary forms;
  - versioned external input for downstream consumers such as
    `bsl-gradual-types`.
- Contract boundary:
  - the bundle is a directory rooted at `form-workspace/`;
  - external consumers may rely on the canonical layout and file-local schemas
    documented here;
  - additive fields are allowed in existing JSON artifacts;
  - unknown fields must be ignored unless a file-local schema says otherwise;
  - unsupported writes must fail closed according to the current writable budget
    and future `support/capabilities.json`;
  - external ingest must not depend on internal AST path conventions except
    where they are explicitly exported through `support/provenance.json`.

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
├── support/
│   ├── capabilities.json
│   ├── provenance.json
│   ├── uncertainty.json
│   └── integration.json
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
- Current source: `formbin unpack`
- Equivalent JSON view: `formbin inspect --json`
- Existing reader path: `formbin inspect <unpack-dir> --json`
- Contract:
  - top-level object;
  - written as `container.inspect.json` at the unpack root;
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
  - current additive top-level summaries:
    - `descriptor_links`
    - `continuation_chains`
    - `pointer_links`
    - `record_layout`
  - current additive per-record keys:
    - `codec`
    - `record_role`
    - `workspace_relative_path`
    - `linked_descriptor_index`
    - `continuation_chain`
  - known descriptor records may add `descriptor_json`;
  - `descriptor_links` is an array of objects with:
    - `label`
    - `descriptor_index`
    - `payload_index`
  - `continuation_chains` is an array of objects with:
    - `kind`
    - `label`
    - `head_record_index`
    - `record_indices`
  - `pointer_links` is an array of objects with:
    - `source_record_index`
    - `target_record_index`
    - `target_header_start`
    - `source_label`
    - `target_label`
  - `record_layout` is an object with:
    - `prefix_size`
    - `total_size`
    - `record_spans`
  - every `record_spans` item is an object with:
    - `index`
    - `header_start`
    - `header_end`
    - `body_start`
    - `body_end`
  - `linked_descriptor_index` points from a known `form` or `module` payload
    record to its matching descriptor record when present;
  - `continuation_chain` is either `null` or the ordered list of record indices
    that participate in a split payload chain for that record;
  - future fields must remain additive and machine-readable.

### `descriptors/form.descriptor.json`

- Status: `bridge`
- Primary owner: `descriptor-json-v1`, consumed by `inspect-rich-json-v1`
- Current exporter: `formbin unpack`
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

- Status: `bridge`
- Primary owner: `descriptor-json-v1`, consumed by `inspect-rich-json-v1`
- Contract:
  - same shape rules as `descriptors/form.descriptor.json`;
  - the artifact name is fixed even when the module record is absent, but the
    file itself is only exported when a module descriptor exists;
  - current workspace export must stay aligned with the inline `descriptor_json`
    summaries exposed by `inspect --json` and `semantic-form`.

## Support Artifacts

Support artifacts stabilize the public bundle boundary for agent edits and
cross-repo ingest. They do not replace the raw/container/semantic artifacts.

### Common Support Rules

- Every `support/*.json` artifact is a top-level object.
- Every artifact must contain:
  - `schema`
  - `version`
- Support metadata must stay deterministic for the same exported workspace.
- Support metadata may reference semantic ids and workspace-relative paths, but
  it must not require consumers to read private Python state.

### `support/capabilities.json`

- Status: `planned`
- Primary owner: `ordinary-form-bundle-v1`
- Schema: `onec-formbin.bundle-capabilities.v1`
- Contract:
  - declares the current workspace mode, supported write paths, and explicit
    read-only areas;
  - must be the machine-readable allowlist for semantic write support;
  - must stay aligned with the writable budget documented in this file.

### `support/provenance.json`

- Status: `planned`
- Primary owner: `ordinary-form-bundle-v1`
- Schema: `onec-formbin.bundle-provenance.v1`
- Contract:
  - maps exported semantic ids and writable fields back to raw/container bridge
    anchors;
  - may expose record indices, workspace-relative paths, and AST paths when
    that is required for deterministic write-back;
  - is the only supported place where AST-path-like write-back anchors may
    cross the public bundle boundary.

### `support/uncertainty.json`

- Status: `planned`
- Primary owner: `ordinary-form-bundle-v1`
- Schema: `onec-formbin.bundle-uncertainty.v1`
- Contract:
  - records coarse bridge confidence, read-only reasons, unsupported areas, and
    variant caveats that affect downstream consumers;
  - keeps partial or heuristic semantics explicit instead of implied.

### `support/integration.json`

- Status: `planned`
- Primary owner: `ordinary-form-bundle-v1`
- Schema: `onec-formbin.bundle-integration.v1`
- Contract:
  - exposes the normalized external ingest surface for downstream semantic
    consumers;
  - must reference `ordinary-form-bundle.v1` and the bundle-local schema
    versions it was built from;
  - must not require downstream consumers to parse raw artifacts or internal AST
    bridge details just to consume ordinary-form semantics.

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

- Status: `bridge`
- Schema: `onec-formbin.form-meta.v1`
- Current precursor: `semantic-form["semantic"]["form.meta.json"]`
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

- Status: `bridge`
- Schema: `onec-formbin.events.v1`
- Current precursor: `semantic-form["semantic"]["events.json"]`
- Contract:
  - required keys:
    - `schema`
    - `version`
    - `items`
  - `items` is an array of objects with:
    - `id`
    - `name`
    - `handler`
    - `scope`
    - `owner_id`
  - current bridge is limited to top-level form-scope events with
    `owner_id = "form-root"` until control ownership is fixture-backed.

### `semantic/commands.json`

- Status: `bridge`
- Schema: `onec-formbin.commands.v1`
- Current precursor: `semantic-form["semantic"]["commands.json"]`
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
  - current bridge is limited to root command definitions that have a matching
    action title in the same AST command section;
  - current bridge exports coarse `owner_id = "form-root"` until control-level
    ownership is fixture-backed.

### `semantic/attributes.json`

- Status: `bridge`
- Schema: `onec-formbin.attributes.v1`
- Current precursor: `semantic-form["semantic"]["attributes.json"]`
- Contract:
  - required keys:
    - `schema`
    - `version`
    - `items`
  - `items` is an array of objects with:
    - `id`
    - `name`
    - `owner_id`
    - `data_path`
    - `type_hint`
    - `role`
  - current bridge is limited to explicit control wrappers whose top-level
    metadata carries an observed `Pattern` marker;
  - `owner_id` points to the current `controls.tree.json` node that owns the
    same explicit wrapper;
  - for the current verified fixtures, `name` and `data_path` come from the
    same explicit control-name source;
  - `type_hint` is currently a raw marker-level hint such as `pattern:#`.

### `semantic/controls.tree.json`

- Status: `bridge`
- Schema: `onec-formbin.controls-tree.v1`
- Current precursor: `semantic-form["semantic"]["controls.tree.json"]`
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
    - `command_ids`
    - `event_bindings`
  - this file owns structure, parent/child hierarchy, and stable node ordering.
  - current bridge is limited to explicit control wrappers observed in the
    verified fixture corpus.

### `semantic/layout.json`

- Status: `bridge`
- Schema: `onec-formbin.layout.v1`
- Current precursor: `semantic-form["semantic"]["layout.json"]`
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
  - current bridge is limited to explicit control child lists with coarse
    `visibility = "unknown"`.

### `semantic/strings.json`

- Status: `bridge`
- Schema: `onec-formbin.strings.v1`
- Current precursor: `semantic-form["semantic"]["strings.json"]`
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
  - current bridge exports AST string-node order while tagging the current
    `form_title`, `event_handler`, `command_name`, `command_title`, and
    `control_name` items with narrower ownership when fixture-backed;
  - all remaining strings stay additive bridge items with coarse ownership.

## Initial Write Budget

The default mode is read-only. The current writable subset exposed by
`safe-semantic-edits-v1` is:

- `semantic/form.meta.json`
  - `form_title` only
- `semantic/events.json`
  - `items[].handler` only for the current form-scope bridge items
- `semantic/commands.json`
  - `items[].name` / `items[].title` only for the current command bridge items
- `semantic/controls.tree.json`
  - `items[].name` / `items[].title` only for current explicit non-root control
    bridge items, and only when both fields stay in sync
- `semantic/attributes.json`
  - `items[].name` / `items[].data_path` only for current explicit
    control-pattern bridge items, and only when both fields stay in sync
- `semantic/strings.json`
  - `items[].value` only when the item is an alias for `form_title`,
    `event_handler`, `command_name`, `command_title`, or current explicit
    `control_name` bridge items

Everything else, including unsupported `attributes.json` fields, structural
`controls.tree.json` fields, and `layout.json`, remains read-only until
fixture-backed evidence justifies it.

## Diff Contract

`semantic-diff-v1` should consume the canonical semantic slice paths from this
document.

The target semantic diff output must:
- stay deterministic;
- preserve the current raw and AST diff modes as fallbacks;
- report changes per semantic slice instead of flattening everything into one
  prose-only blob;
- prefer materialized `semantic/*.json` workspace slices when diffing unpack
  dirs whose raw form payload is unchanged;
- fall back to rebuilt semantic slices from the raw form payload when the raw
  form bytes changed or materialized semantic slices are absent.

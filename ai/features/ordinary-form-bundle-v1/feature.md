# Ordinary Form Bundle V1

Stabilize a public versioned ordinary-form workspace bundle so an agent can
export a `Form.bin` into understandable artifacts, edit the supported semantic
surface, apply those edits safely, and pack the result back into `Form.bin`.

This pack is responsible for evolving toward:
- a public `ordinary-form-bundle.v1` contract rooted at `form-workspace/`;
- explicit support metadata for writable scope, provenance, and uncertainty;
- an external ingest surface that downstream tools can consume without binding
  to `onec-formbin` internals.

Current verified baseline inside this pack:
- `unpack` already writes the current container backbone, descriptor JSON, and
  semantic/support workspace artifacts on the verified fixtures;
- `semantic-form` already matches between a source `Form.bin` and its unpacked
  workspace on the baseline fixture;
- `apply-semantic` already refreshes the current support artifacts after the
  supported edit subset and still fails closed on split-form workspaces.

Use this pack when a change touches:
- `docs/workspace-contract.md`
- `src/onec_formbin/api.py`
- `src/onec_formbin/semantic_form.py`
- CLI commands that export, apply, or repack ordinary-form workspaces
- tests and docs that define the public bundle contract

Out of scope:
- replacing the raw-first codec with semantic-only rebuilds;
- broadening support claims beyond the verified fixture corpus;
- making split-form writes succeed before continuation-safe evidence exists;
- embedding canonical type-system ownership that belongs in
  `bsl-gradual-types`.

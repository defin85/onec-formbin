# Ordinary Form Bundle V1 Pack

Use this feature pack to stabilize the public versioned ordinary-form workspace
bundle for agent editing and external ingest.

Cross-pack source of truth: `docs/workspace-contract.md`.

Current stage:
- the current raw/container/descriptor/semantic workspace ladder already exists;
- narrow semantic writes are still owned by `safe-semantic-edits-v1`;
- the public `ordinary-form-bundle.v1` contract and `support/*.json` metadata
  now materialize during `unpack` and refresh during supported
  `apply-semantic` flows without weakening the raw-first safety boundary.

Target outcome:
- publish a versioned ordinary-form workspace bundle rooted at
  `form-workspace/`;
- make the export/edit/apply/pack flow explicit for agent-driven form changes;
- provide a stable external input for downstream consumers such as
  `bsl-gradual-types`.

Split intent:
- `dev.jsonl`: guard the baseline bundle backbone, support metadata, and
  current pack-safe edit/apply path on the editable fixture;
- `holdout.jsonl`: confirm split-form readability and fail-closed behavior on
  the verified holdout fixture.

Typical flow:
1. `make validate-feature FEATURE=ordinary-form-bundle-v1`
2. `make feature-start FEATURE=ordinary-form-bundle-v1`
3. `make feature-baseline FEATURE=ordinary-form-bundle-v1 RUN_ID=<run-id>`
4. Tighten the bundle contract in `docs/workspace-contract.md` before changing
   behavior or widening the workspace surface.
5. Add or replace guards only with repo-owned commands and fixture-backed
   evidence.

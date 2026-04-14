# Feature Packs

Store eval-driven feature work under `ai/features/<feature-id>/`.

Starter pack:
- `TEMPLATE`: copy to a real feature id and replace all placeholders before use.

Primary product pack:
- `raw-first-guard`: default pack for the repository's main feature, parsing
  `Form.bin` through the raw-first workflow.

Slice guards:
- `container-core-guard`: protects low-level container parsing, inspect,
  unpack/pack, roundtrip, and size-policy behavior.
- `form-ast-guard`: protects the experimental AST workflow for `parse-form`,
  `build-form`, and AST-backed diff rendering.

Planned roadmap packs:
- `descriptor-json-v1`: structured JSON decoding for descriptor records.
- `inspect-rich-json-v1`: richer machine-readable `inspect --json` contract and
  the future `container.inspect.json` backbone.
- `form-semantic-model-v1`: semantic JSON model and future `semantic/` slice
  exports on top of the current AST path.
- `safe-semantic-edits-v1`: narrow, explicit writes from semantic workspace
  slices back to raw artifacts with raw-first safety.
- `semantic-diff-v1`: semantic form diff for workspace slices beyond raw and AST renderings.
- `ordinary-form-bundle-v1`: public versioned ordinary-form workspace bundle
  contract for agent editing and external ingest.
- `variant-support-matrix-v1`: fixture-backed rollout of additional container variants.
- `repack-policy-expand-v1`: more safe repack cases backed by fixture evidence.
- `ast-fidelity-v1`: better rebuild fidelity for `parse-form` / `build-form`.
- `diagnostics-v1`: clearer CLI diagnostics and failure-path contracts.

LLM-editable workspace ladder:
1. `inspect-rich-json-v1` builds the container backbone.
2. `form-semantic-model-v1` exports semantic slices.
3. `safe-semantic-edits-v1` makes a narrow subset of those slices writable.
4. `semantic-diff-v1` diffs those slices for review and regression control.
5. `ordinary-form-bundle-v1` fixes the external `ordinary-form-bundle.v1`
   contract and support metadata for cross-repo consumers.

Cross-pack source of truth:
- `docs/workspace-contract.md` fixes the canonical artifact names, ownership
  boundaries, and minimum schemas for this ladder.

Roadmap scaffolds:
- Some packs already own partial implemented behavior, others are still starter scaffolds.
- Their starter manifests always guard the nearest currently verified behavior.
- Tighten each pack with feature-specific fixtures, goldens, or wrapper commands before calling the feature delivered.

Recommended flow:
1. For general product work, start with `raw-first-guard`.
2. On a new session, run `make feature-resume FEATURE=<feature-id>` before starting a new run.
3. Switch to a slice guard only when the change stays clearly inside that subsystem.
4. Copy `ai/features/TEMPLATE/` to a real feature id when you need a new managed stream.
5. Fill `feature.md`, `change-constraints.md`, and `checklist.md`.
6. Use repo-owned verification commands in `dev.jsonl` and `holdout.jsonl`.
7. Run `make validate-feature FEATURE=<feature-id>`.
8. Start a run only when `feature-resume` reports that no prior run exists; `make feature-start` fails closed otherwise.

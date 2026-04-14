# Variant Support Matrix V1 Pack

Use this feature pack for roadmap work on a disciplined support matrix for
additional `Form.bin` variants.

Current stage:
- the current three-fixture matrix is now mirrored explicitly across
  `README.md`, `docs/verification.md`, and `tests/fixtures/README.md`;
- the manifests keep that documented matrix green while new variants are still
  out of scope.

Target outcome:
- add new fixture-backed variants without weakening existing guarantees;
- make the support matrix explicit in docs and process assets;
- keep dev versus holdout boundaries clear when new variants are introduced.

Split intent:
- `dev.jsonl`: baseline guards on the documented fixture matrix and normal fixtures;
- `holdout.jsonl`: confirmation on the complex split-form variant after a candidate is kept.

Typical flow:
1. `make validate-feature FEATURE=variant-support-matrix-v1`
2. `make feature-start FEATURE=variant-support-matrix-v1`
3. `make feature-baseline FEATURE=variant-support-matrix-v1 RUN_ID=<run-id>`
4. Add new variants only with explicit fixture and docs updates.
5. Tighten the manifests as the support matrix evolves.

# Feature Packs

Store eval-driven feature work under `ai/features/<feature-id>/`.

Current managed pack:
- `raw-first-guard`: protects raw-first container behavior, CLI smoke, and
  fixture-backed holdout coverage.

Recommended flow:
1. Create a real feature directory under `ai/features/`.
2. Fill `feature.md`, `change-constraints.md`, and `checklist.md`.
3. Use repo-owned verification commands in `dev.jsonl` and `holdout.jsonl`.
4. Run `make validate-feature FEATURE=<feature-id>`.
5. Start a run and use the loop commands from `Makefile`.

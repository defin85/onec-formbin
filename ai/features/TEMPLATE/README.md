# Feature Pack Template

Copy this directory to `ai/features/<feature-id>/` and replace the placeholders.

Required files:
- `feature.md`
- `change-constraints.md`
- `checklist.md`
- `dev.jsonl`
- `holdout.jsonl`

Supported case modes:
- command-based `verification` commands that call repo-owned wrappers;
- pure `input` / `expected` cases evaluated through `scripts/feature_loop_adapter.py`.

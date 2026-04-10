# Recommended Skills

This file is the compact first-hour routing layer for common workflows.

## Recommended Global Skills

- `coder`: use for implementing the feature or adjusting the repo-owned process layer.
- `reviewer`: use for adversarial review of a completed or suspicious change.
- `1c-guidance`: use when repository work depends on 1C platform context or terminology.
- `autonomous-feedback-loop`: use when the main problem is discovering verified debug, test, restart, or hot-reload paths.
- `autoresearch-loop`: use when available for eval-driven feature work through feature packs and repo-owned loop commands.

## Repo-Owned Entry Points

- `make codex-onboard`
- `make agent-verify`
- `make validate-feature FEATURE=<feature-id>`
- `make feature-start FEATURE=<feature-id>`
- `make feature-baseline FEATURE=<feature-id> RUN_ID=<run-id>`
- `make feature-iteration FEATURE=<feature-id> RUN_ID=<run-id>`
- `make feature-holdout FEATURE=<feature-id> RUN_ID=<run-id>`
- `make feature-ci-replay RUN_ID=<run-id> [PHASE=both]`

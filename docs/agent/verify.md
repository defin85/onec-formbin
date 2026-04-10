# Verify

## Baseline

First safe verification path:

```bash
make agent-verify
```

This should confirm:
- agent-facing docs exist and link correctly;
- feature-pack manifests have the required shape;
- loop scripts compile cleanly;
- the CLI smoke path still works on a known fixture.

For behavior changes, continue with the repo checks from
[docs/verification.md](../verification.md).

## Feature Loop

For a feature pack under `ai/features/<feature-id>/`:

```bash
make validate-feature FEATURE=<feature-id>
make feature-start FEATURE=<feature-id>
make feature-baseline FEATURE=<feature-id> RUN_ID=<run-id>
make feature-iteration FEATURE=<feature-id> RUN_ID=<run-id>
make feature-holdout FEATURE=<feature-id> RUN_ID=<run-id>
make feature-ci-replay RUN_ID=<run-id> [PHASE=both]
```

Current dogfood feature pack:

```bash
make validate-feature FEATURE=raw-first-guard
```

Use the repo's own wrapper commands inside the feature manifests whenever
possible. If a feature pack uses pure `input -> expected` cases, either keep
`scripts/feature_loop_adapter.py` and set `adapter_callable` in the cases, or
replace `scripts/feature_loop_adapter.py` with a repo-specific adapter.

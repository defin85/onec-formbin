# Verification Guide

Use the smallest relevant check first, then the full repo checks when behavior
changes.

## Bootstrap

```bash
uv sync
make agent-verify
```

Run this in a fresh clone before any `uv run ...` command.

## CLI smoke checks

```bash
uv run formbin inspect tests/fixtures/common-indicator.Form.bin
uv run formbin roundtrip-check tests/fixtures/common-indicator.Form.bin
```

Expected results:

- `inspect` exits with code `0` and prints the record list
- `roundtrip-check` exits with code `0` and prints `roundtrip ok`

## Full repo checks

```bash
uv run ruff check .
uv run pytest
```

Run both after any behavior change.

## Targeted guidance

- Parser or repack changes:
  - run `uv run pytest tests/test_roundtrip.py tests/test_pack_limits.py`
- Diff changes:
  - run `uv run pytest tests/test_diff.py`
- AST changes:
  - run `uv run pytest tests/test_form_ast.py`
- Docs-only changes:
  - at minimum run `uv run formbin inspect tests/fixtures/common-indicator.Form.bin`

## Eval-driven feature loop

For managed feature work:

```bash
make codex-onboard
make validate-feature FEATURE=<feature-id>
make feature-start FEATURE=<feature-id>
make feature-baseline FEATURE=<feature-id> RUN_ID=<run-id>
make feature-iteration FEATURE=<feature-id> RUN_ID=<run-id>
make feature-holdout FEATURE=<feature-id> RUN_ID=<run-id>
make feature-ci-replay RUN_ID=<run-id> PHASE=both
```

Use the feature pack manifests under `ai/features/` as the source of truth for
dev versus holdout checks.

## When docs must change too

Update `README.md` and `tests/fixtures/README.md` when:

- install or verification commands change
- support claims change
- fixture coverage or known limitations change

# Verification Guide

Use the smallest relevant check first, then the full repo checks when behavior
changes.

## Bootstrap

```bash
uv sync
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

## When docs must change too

Update `README.md` and `tests/fixtures/README.md` when:

- install or verification commands change
- support claims change
- fixture coverage or known limitations change

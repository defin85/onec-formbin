# Project Map

This file is the curated process-layer map for `onec-formbin`.

## Repository Identity

- Standalone tool for inspecting, unpacking, repacking, and diffing 1C
  ordinary-form `Form.bin` containers.
- Primary subsystem: the raw-first container codec in `src/onec_formbin/`.

## Known Source Roots

- `src/onec_formbin/`: package source and CLI entry points.
- `tests/`: fixture-backed behavior tests.
- `tests/fixtures/`: verified support corpus and fixture notes.
- `README.md`, `docs/repo-map.md`, `docs/verification.md`, `code_review.md`:
  human and agent-facing truth.
- `uv run formbin ...`: CLI entry point.

## Canonical Entry Points

- `make codex-onboard`
- `make agent-verify`
- `docs/repo-map.md`
- `docs/verification.md`
- `scripts/feature_loop.py`
- `scripts/feature_loop_core.py`
- `scripts/feature_loop_adapter.py`
- `ai/features/`

## High-Risk Areas

- `src/onec_formbin/container.py`: record parsing and header policy.
- `src/onec_formbin/api.py`: unpack/pack/roundtrip workflow.
- `src/onec_formbin/diffing.py`: diff rendering and exit behavior.
- `src/onec_formbin/form_ast.py`: experimental layer that must stay separate
  from the raw-first codec.
- `tests/fixtures/`: support boundary and local corpus.

## Next Updates

- Keep `docs/verification.md` and the managed feature packs aligned.
- Add more feature packs only when they map to real change streams.

# Repo Instructions

## Language
- Keep code, docs, and CLI messages in English.
- Keep user-facing status updates concise.

## Scope
- This repo is a standalone tool for inspecting, unpacking, and repacking 1C `Form.bin` containers.
- Favor lossless raw handling over speculative semantic rewriting.

## Editing rules
- Read the relevant files before editing.
- Prefer minimal changes with tests.
- Do not silently broaden support claims beyond verified fixtures.

## Verification
- Run `uv run pytest` for behavior changes.
- Run `uv run ruff check .` for linting.
- If a limitation remains, document it in `README.md`.


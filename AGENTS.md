# Repo Instructions

## Language
- Keep code, docs, and CLI messages in English.
- Keep user-facing status updates concise.

## Scope
- This repo is a standalone tool for inspecting, unpacking, and repacking 1C `Form.bin` containers.
- Favor lossless raw handling over speculative semantic rewriting.

## Repo map
- `src/onec_formbin/cli.py`: Typer entry point and CLI contract.
- `src/onec_formbin/api.py`: high-level inspect/unpack/pack/roundtrip workflow.
- `src/onec_formbin/container.py`: low-level container parsing and header rendering.
- `src/onec_formbin/diffing.py`: diff pipeline for `Form.bin` files and unpack directories.
- `src/onec_formbin/form_ast.py`: experimental `form.raw <-> AST` layer; keep separate from the raw-first codec.
- `tests/`: fixture-backed behavior coverage.
- `docs/adr/0001-raw-first.md`: architecture decision for raw-first handling.
- `docs/repo-map.md`, `docs/verification.md`, `code_review.md`: agent-facing references for navigation, verification, and review.

## Setup
- Run `uv sync` before first use in a fresh clone.
- Use `uv run formbin ...` for CLI commands.

## Search
- Search order: `mcp__claude-context__search_code` if available -> `rg` -> `rg --files` -> targeted file reads.
- Start with narrow queries and restrict early to `src/onec_formbin/`, `tests/`, `docs/`, `README.md`, and `AGENTS.md`.
- Confirm important implementation facts in at least two sources: code + test/doc.
- Do not treat TODO lists, plans, task status, or support claims in docs as proof that behavior is implemented.

## Editing rules
- Read the relevant files before editing.
- Prefer minimal changes with tests.
- Do not silently broaden support claims beyond verified fixtures.

## Verification
- Run `uv run pytest` for behavior changes.
- Run `uv run ruff check .` for linting.
- Run `uv run formbin inspect tests/fixtures/common-indicator.Form.bin` as the basic CLI smoke check.
- If a limitation remains, document it in `README.md`.

## Definition of done
- Keep `README.md`, `docs/verification.md`, and fixture coverage notes in sync with real behavior.
- Follow `code_review.md` when preparing or reviewing non-trivial changes.

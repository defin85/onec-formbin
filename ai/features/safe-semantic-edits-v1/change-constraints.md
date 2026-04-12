# Change Constraints

- Keep mirror-safe edits packable and preserve-policy size changes rejected unless explicitly justified and fixture-backed.
- Do not tune on `ai/features/safe-semantic-edits-v1/holdout.jsonl`.
- Do not edit `tests/fixtures/*.Form.bin` during iteration.
- Add semantic-edit fixtures or expected outputs before claiming edit support.
- Keep semantic edits narrow, field-scoped, and easy to diff in workspace files.
- Keep the semantic-edit path optional and separate from the core raw-first codec.
- If semantic edit behavior becomes user-facing, update `README.md`,
  `docs/verification.md`, and `tests/fixtures/README.md` together.

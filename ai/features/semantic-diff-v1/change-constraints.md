# Change Constraints

- Keep the current raw and AST diff routes working while semantic diff is added.
- Do not tune on `ai/features/semantic-diff-v1/holdout.jsonl`.
- Do not edit `tests/fixtures/*.Form.bin` during iteration.
- Add semantic diff fixtures or expected outputs before claiming semantic diff coverage.
- Prefer deterministic machine-readable diff artifacts over prose-only output.
- Keep diff exit-code behavior stable unless the CLI contract is intentionally changed.
- If diff output or guarantees change, update `README.md` and `docs/verification.md` together.

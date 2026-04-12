# Change Constraints

- Keep the AST layer experimental and separate from the core raw-first codec.
- Do not tune on `ai/features/form-ast-guard/holdout.jsonl`.
- Do not edit `tests/fixtures/*.Form.bin` during iteration.
- Do not broaden AST support claims in `README.md` or `tests/fixtures/README.md`
  without verified fixture evidence.
- Preserve split-form continuation handling for the verified fixture corpus.
- If AST workflow or support claims change, update `README.md`,
  `docs/verification.md`, and `tests/fixtures/README.md` together.

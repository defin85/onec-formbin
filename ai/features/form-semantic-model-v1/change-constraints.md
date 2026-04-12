# Change Constraints

- Keep the raw-first codec and AST workflow working while the semantic model evolves.
- Do not tune on `ai/features/form-semantic-model-v1/holdout.jsonl`.
- Do not edit `tests/fixtures/*.Form.bin` during iteration.
- Do not claim full ordinary-form semantics; this feature exports a summary model in v1.
- Prefer additive semantic slices over replacing the current export with one giant unstable blob.
- Keep split-form continuation handling intact for the verified corpus.
- If semantic outputs become user-facing, update `README.md`,
  `docs/verification.md`, and `tests/fixtures/README.md` together.

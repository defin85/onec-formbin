# Change Constraints

- Keep structural AST roundtrip green while fidelity work is added.
- Do not tune on `ai/features/ast-fidelity-v1/holdout.jsonl`.
- Do not edit `tests/fixtures/*.Form.bin` during iteration.
- Add fidelity-specific goldens or metrics before claiming improved rebuild fidelity.
- Keep the AST layer optional and separate from raw-first repack safety.
- Update `README.md`, `docs/verification.md`, and `tests/fixtures/README.md` together if AST fidelity guarantees change.

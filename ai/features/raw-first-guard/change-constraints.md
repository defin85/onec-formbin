# Change Constraints

- Keep the raw-first codec conservative and lossless for known fixtures.
- Do not tune on `ai/features/raw-first-guard/holdout.jsonl`.
- Do not edit `tests/fixtures/*.Form.bin` during iteration.
- Do not broaden support claims in `README.md` or `tests/fixtures/README.md`
  without verified fixture evidence.
- Keep the experimental AST layer separate from the core pack/unpack path.
- If workflow or support claims change, update `README.md`,
  `docs/verification.md`, and `tests/fixtures/README.md` together.

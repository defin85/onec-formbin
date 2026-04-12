# Change Constraints

- Keep the raw-first codec conservative and lossless for known fixtures.
- Do not tune on `ai/features/container-core-guard/holdout.jsonl`.
- Do not edit `tests/fixtures/*.Form.bin` during iteration.
- Keep pointer metadata stable for verified split-form fixtures.
- Keep unsafe size-changing edits rejected for preserve-policy records.
- Do not broaden support claims in `README.md` or `tests/fixtures/README.md`
  without verified fixture evidence.
- If codec workflow or support claims change, update `README.md`,
  `docs/verification.md`, and `tests/fixtures/README.md` together.

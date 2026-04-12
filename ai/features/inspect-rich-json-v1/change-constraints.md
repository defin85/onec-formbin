# Change Constraints

- Keep the existing `inspect --json` contract stable while richer fields are added.
- Do not tune on `ai/features/inspect-rich-json-v1/holdout.jsonl`.
- Do not edit `tests/fixtures/*.Form.bin` during iteration.
- Add or update JSON assertions or goldens before claiming richer inspect coverage.
- Keep raw-first roundtrip safety independent from richer inspect rendering.
- Prefer additive machine-readable fields over reshaping the whole output at once.
- If inspect output changes for users, update `README.md` and `docs/verification.md` together.

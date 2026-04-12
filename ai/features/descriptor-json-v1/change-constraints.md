# Change Constraints

- Keep descriptor records detectable through the current raw-first workflow while JSON decoding is added.
- Do not tune on `ai/features/descriptor-json-v1/holdout.jsonl`.
- Do not edit `tests/fixtures/*.Form.bin` during iteration.
- Do not claim semantic meaning for undocumented descriptor integers.
- Keep unknown descriptor bodies lossless and surface them through opaque fallback output.
- Keep no-op repack behavior lossless for the verified corpus.
- If descriptor JSON becomes user-facing, update `README.md`,
  `docs/verification.md`, and `tests/fixtures/README.md` together.

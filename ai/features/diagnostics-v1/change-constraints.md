# Change Constraints

- Keep normal CLI success paths working while diagnostics are improved.
- Do not tune on `ai/features/diagnostics-v1/holdout.jsonl`.
- Do not edit `tests/fixtures/*.Form.bin` during iteration.
- Add stderr snapshots or explicit output assertions before claiming diagnostics improvements.
- Keep failure paths non-successful unless the CLI contract intentionally changes.
- Update `README.md` and `docs/verification.md` together if diagnostics or exit-code behavior changes.

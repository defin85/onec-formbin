# Change Constraints

- Keep the raw-first unpack/pack workflow as the safety boundary for rebuilds.
- Do not tune on `ai/features/ordinary-form-bundle-v1/holdout.jsonl`.
- Do not edit `tests/fixtures/*.Form.bin` during iteration.
- Do not silently widen writable scope beyond the documented allowlist.
- Keep public bundle schemas additive and deterministic.
- Do not couple the public bundle contract to internal Python objects or hidden
  AST conventions outside explicit support metadata.
- If bundle guarantees or artifact names change, update `README.md`,
  `docs/workspace-contract.md`, and `tests/fixtures/README.md` together.

# Repack Policy Expand V1 Pack

Use this feature pack for roadmap work on expanding safe repack behavior.

Current stage:
- the pack now guards no-op repack plus the current verified mirror-safe module
  and form payload edits on `common-print-form.Form.bin`;
- preserve-policy refusal on the non-mirror holdout fixture remains protected.

Target outcome:
- support more safe size-changing edits where fields can be recomputed;
- keep preserve-policy refusals explicit where semantics remain unknown;
- expand repack support only through fixture-backed evidence.

Split intent:
- `dev.jsonl`: baseline guards on mirror-safe repack and no-op pack/unpack;
- `holdout.jsonl`: confirmation on preserve-policy behavior after a candidate is kept.

Typical flow:
1. `make validate-feature FEATURE=repack-policy-expand-v1`
2. `make feature-start FEATURE=repack-policy-expand-v1`
3. `make feature-baseline FEATURE=repack-policy-expand-v1 RUN_ID=<run-id>`
4. Add one new safe repack case at a time with fixture evidence.
5. Tighten the manifests as new policy cases become verified.

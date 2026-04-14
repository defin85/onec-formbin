# AST Fidelity V1 Pack

Use this feature pack for roadmap work on improving the fidelity of the
`parse-form` / `build-form` cycle.

Current stage:
- the pack now guards structural AST roundtrip plus a first canonical-build
  fixed-point check on `common-print-form.Form.bin`;
- fidelity work is still explicitly short of byte-identical source rebuild
  claims.

Target outcome:
- reduce churn between parsed and rebuilt `form.raw`;
- keep structural AST stability while improving textual fidelity;
- prepare tighter metrics for format-preserving rebuilds.

Split intent:
- `dev.jsonl`: baseline structural and CLI roundtrip guards on the main AST fixture;
- `holdout.jsonl`: confirmation on an alternate fixture after a candidate is kept.

Typical flow:
1. `make validate-feature FEATURE=ast-fidelity-v1`
2. `make feature-start FEATURE=ast-fidelity-v1`
3. `make feature-baseline FEATURE=ast-fidelity-v1 RUN_ID=<run-id>`
4. Add fidelity metrics or goldens in small reversible steps.
5. Replace starter guards with stricter fidelity checks as they become reliable.

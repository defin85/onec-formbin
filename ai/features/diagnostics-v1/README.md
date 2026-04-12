# Diagnostics V1 Pack

Use this feature pack for roadmap work on CLI diagnostics, error reporting, and
failure-path contracts.

Current stage:
- roadmap scaffold;
- the starter manifests keep current success and failure-path exits green until
  explicit diagnostics snapshots or output contracts are added.

Target outcome:
- clearer CLI failures for common user mistakes and unsupported edits;
- stable exit codes and machine-readable diagnostics where appropriate;
- reduced reliance on raw tracebacks in normal error paths.

Split intent:
- `dev.jsonl`: baseline success and failure-path guards on common errors;
- `holdout.jsonl`: confirmation on the preserve-policy error path after a candidate is kept.

Typical flow:
1. `make validate-feature FEATURE=diagnostics-v1`
2. `make feature-start FEATURE=diagnostics-v1`
3. `make feature-baseline FEATURE=diagnostics-v1 RUN_ID=<run-id>`
4. Add explicit diagnostics expectations in small reversible steps.
5. Tighten the manifests with stderr snapshots or JSON diagnostics once designed.

# Diagnostics V1 Pack

Use this feature pack for roadmap work on CLI diagnostics, error reporting, and
failure-path contracts.

Current stage:
- the normal inspect success path remains covered;
- missing-input `inspect` and wrong-path `apply-semantic` calls now produce
  one-line CLI errors without traceback;
- missing semantic workspace slices on `apply-semantic` now stay on the same
  controlled error path;
- unsupported `controls.tree.json[].event_bindings` edits on `apply-semantic`
  now stay on the same controlled error path;
- unsupported `layout.json` edits on `apply-semantic` now stay on the same
  controlled error path;
- unsupported `attributes.json.owner_id` edits on `apply-semantic` now stay on
  the same controlled error path;
- unsupported `form.meta.json` non-title edits, `events.json` non-handler
  edits, `commands.json` non-title edits, and read-only `strings.json` role
  edits on `apply-semantic` now stay on the same controlled error path;
- `pack` on a directory without `manifest.json` now stays on the same
  controlled workspace-validation path;
- the preserve-policy holdout refusal remains the protected confirmation path.

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

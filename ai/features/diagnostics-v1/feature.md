# Diagnostics V1

Improve CLI diagnostics, error handling, and failure-path contracts for the
current raw-first workflow.

This roadmap feature is intended to evolve toward:
- user-facing errors that explain what failed and why;
- stable exit-code behavior across normal failure modes;
- explicit diagnostics for unsupported edits and missing inputs.

Current scaffold state:
- the manifests currently guard that key failure modes stay non-successful and
  that the normal inspect path still works;
- before claiming better diagnostics, add stderr snapshots or stricter output contracts.

Use this pack when a change touches:
- `src/onec_formbin/cli.py`
- `src/onec_formbin/api.py`
- `src/onec_formbin/container.py`
- tests or docs that define CLI error behavior

Out of scope:
- changing core parse or repack behavior without matching diagnostic tests;
- editing holdout fixtures during tuning;
- claiming polished diagnostics without fixture-backed output checks.

# AST Fidelity V1

Improve how closely rebuilt `form.raw` matches the source while preserving the
current AST structure guarantees.

This roadmap feature is intended to evolve toward:
- fewer formatting changes after `parse-form` and `build-form`;
- fixture-backed fidelity metrics for rebuilt form text;
- a clearer boundary between structural stability and textual fidelity.

Current scaffold state:
- the manifests currently guard structural AST stability and CLI parse/build roundtrip;
- before claiming fidelity improvements, add fidelity-specific goldens or metrics.

Use this pack when a change touches:
- `src/onec_formbin/form_ast.py`
- `src/onec_formbin/diffing.py`
- CLI behavior for `parse-form` or `build-form`
- tests or docs that define AST fidelity expectations

Out of scope:
- full semantic parsing of ordinary forms;
- byte-identical claims without fixture-backed evidence;
- editing holdout fixtures during tuning.

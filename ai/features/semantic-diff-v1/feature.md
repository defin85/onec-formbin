# Semantic Diff V1

Introduce a semantic diff layer for form changes while preserving the current
raw-first diff pipeline and making the semantic workspace reviewable.

This pack is responsible for evolving toward:
- semantic change reporting for ordinary forms;
- stable diff outputs for workspace slices such as `form.meta.json`,
  `events.json`, `commands.json`, `attributes.json`, `controls.tree.json`,
  `layout.json`, and `strings.json`;
- compatibility with the current raw and AST diff modes as fallbacks.

Current verified baseline inside this pack:
- raw diff still reports identical and changed inputs correctly;
- AST-backed diff still works;
- the split-form fixture still passes identical-input diff checks.

Use this pack when a change touches:
- `src/onec_formbin/diffing.py`
- `src/onec_formbin/form_ast.py`
- `src/onec_formbin/semantic_form.py`
- future semantic-diff modules under `src/onec_formbin/`
- CLI behavior for `formbin diff`

Out of scope:
- changing raw-first repack safety guarantees;
- editing holdout fixtures during tuning;
- claiming semantic understanding without fixture-backed evidence.

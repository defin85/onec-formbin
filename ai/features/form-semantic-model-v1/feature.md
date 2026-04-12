# Form Semantic Model V1

Introduce an experimental semantic JSON summary for ordinary forms on top of the
current raw-first and AST workflow, then evolve it into the `semantic/` slice
layer of the LLM-editable workspace.

This feature currently covers:
- a `semantic-form` CLI export for `Form.bin`, unpack dirs, and `form.raw`;
- container-level summaries for descriptor, module, and form records when available;
- AST-derived structure metrics such as node counts, top-level shape, and string samples;
- compatibility with split-form continuation handling on the verified corpus.

This pack is responsible for evolving that summary toward:
- `form.meta.json` for top-level form properties;
- `events.json`, `commands.json`, `attributes.json`, and `strings.json`;
- `controls.tree.json` and `layout.json` for structure and placement;
- a semantic export that is directly usable by downstream semantic diff and edit flows.

Use this pack when a change touches:
- `src/onec_formbin/semantic_form.py`
- `src/onec_formbin/form_ast.py`
- future semantic-model modules under `src/onec_formbin/`
- `src/onec_formbin/cli.py` for semantic export commands
- tests or fixtures that define semantic-model outputs

Out of scope:
- broadening support claims beyond verified fixtures;
- making semantic parsing mandatory for the raw-first unpack/pack codec;
- semantic editing or rebuild from the semantic JSON model;
- editing holdout fixtures during tuning.

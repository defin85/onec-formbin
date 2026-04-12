# Safe Semantic Edits V1

Introduce a narrow, explicit semantic edit surface for ordinary forms while
keeping the raw-first codec conservative and making the semantic workspace
directly editable by an LLM.

This pack is responsible for evolving toward:
- structured edits for a limited set of understood form properties from
  `form.meta.json`, `events.json`, `commands.json`, `attributes.json`,
  `controls.tree.json`, and `strings.json`;
- safe conversion from semantic changes back into raw artifacts such as
  `form.raw` and `module.bsl`;
- clear refusal behavior for edits that would violate repack safety.

Current verified baseline inside this pack:
- AST rebuilds still work;
- mirror-safe module edits still repack;
- preserve-policy size changes still fail safely.

Use this pack when a change touches:
- `src/onec_formbin/form_ast.py`
- future semantic-edit modules under `src/onec_formbin/`
- `src/onec_formbin/api.py` for repack safety on semantic edits
- CLI commands that apply or export structured edits

Out of scope:
- arbitrary semantic rewriting of unsupported form variants;
- weakening preserve-policy safeguards;
- making semantic edits mandatory for the raw-first codec;
- editing holdout fixtures during tuning.

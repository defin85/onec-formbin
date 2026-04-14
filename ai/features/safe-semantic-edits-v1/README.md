# Safe Semantic Edits V1 Pack

Use this feature pack for the controlled write path from the future semantic
workspace back to raw editable artifacts.

Cross-pack source of truth: `docs/workspace-contract.md`.

Current stage:
- the first opt-in semantic edit command now exists for unpack dirs;
- the current writable subset covers `semantic/form.meta.json.form_title`, current form-scope `semantic/events.json[].handler`, and current `semantic/commands.json[].title`;
- the current writable subset now also covers direct `semantic/controls.tree.json[].name/title` edits for explicit non-root control bridge items;
- the current writable subset now also covers direct `semantic/attributes.json[].name/data_path` edits for current explicit control-pattern bridge items when both fields stay in sync;
- `semantic/strings.json[].value` is now writable only as an alias for those
  same fixture-backed roles plus current explicit `control_name` bridge items;
- the user-facing `apply-semantic` CLI flow is now fixture-backed for both the
  original form-title path, the current command-title and event-handler paths,
  the current direct attribute-rename path, and the current explicit
  `control_name` alias path;
- the user-facing `apply-semantic` CLI flow is now also fixture-backed for the
  supported `strings.json` alias path that updates form title, event handler,
  and command title together;
- the command refreshes `semantic/*.json` after applying a supported semantic edit;
- split-form workspaces and unsupported field changes such as non-title
  `form.meta.json` edits, `layout.json`, or `controls.tree.json[].event_bindings`
  metadata still fail closed.

Target outcome:
- allow a narrow class of semantic edits through `semantic/` slice files;
- rebuild only the affected raw artifacts such as `raw/form.raw` and
  `raw/module.bsl` when that is safe and fixture-backed;
- keep repack safety rules explicit and conservative;
- prepare a path from semantic model to controlled write support.

Split intent:
- `dev.jsonl`: baseline guards on AST build and current edit-adjacent behavior
  while semantic writes are added;
- `holdout.jsonl`: confirmation on preserve-policy and split-form behavior after
  a candidate is kept.

Typical flow:
1. `make validate-feature FEATURE=safe-semantic-edits-v1`
2. `make feature-start FEATURE=safe-semantic-edits-v1`
3. `make feature-baseline FEATURE=safe-semantic-edits-v1 RUN_ID=<run-id>`
4. Add narrow semantic-edit capabilities in small reversible steps.
5. Replace starter guards with semantic-edit fixtures once the edit surface exists.

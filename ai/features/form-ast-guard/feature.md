# Form AST Guard

Protect the experimental AST workflow while iterating on `onec-formbin`.

This managed feature pack covers:
- parsing a known `form` payload into AST JSON through `parse-form`;
- rebuilding `form.raw` from AST JSON through `build-form`;
- AST-backed diff rendering through `formbin diff --form-mode ast`;
- split-form continuation handling when the form payload continues in a later record.

Use this pack when a change touches:
- `src/onec_formbin/form_ast.py`
- `src/onec_formbin/diffing.py`
- `src/onec_formbin/cli.py` for `parse-form`, `build-form`, or `--form-mode ast`

Out of scope:
- making the AST layer required for the raw-first unpack/pack codec;
- semantic understanding of ordinary-form concepts;
- byte-identical reconstruction of original `form.raw` formatting;
- adding support claims for undocumented container variants without fixture evidence.

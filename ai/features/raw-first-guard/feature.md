# Raw-First Guard

Protect the raw-first container workflow while iterating on `onec-formbin`.

This managed feature pack covers:
- inspect and roundtrip behavior on known fixtures;
- raw-first pack safety and size-policy enforcement;
- diff and experimental AST behavior on the verified corpus.

Use this pack when a change touches:
- `src/onec_formbin/container.py`
- `src/onec_formbin/api.py`
- `src/onec_formbin/diffing.py`
- `src/onec_formbin/form_ast.py`
- CLI behavior that changes `inspect`, `roundtrip-check`, or `diff`

Out of scope:
- adding support claims for new undocumented container variants without fixtures;
- making the experimental AST layer mandatory for the raw-first codec;
- changing fixture files as part of tuning.

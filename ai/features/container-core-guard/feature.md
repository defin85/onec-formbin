# Container Core Guard

Protect the low-level raw-first container workflow while iterating on
`onec-formbin`.

This managed feature pack covers:
- deterministic container parsing and record metadata exposure through `inspect`;
- unpacking container records into a manifest + workspace tree;
- repacking unpacked workspaces back into `Form.bin`;
- exact no-op roundtrip on the managed fixtures;
- mirror versus preserve size-policy handling during repack.

Use this pack when a change touches:
- `src/onec_formbin/container.py`
- `src/onec_formbin/api.py`
- `src/onec_formbin/workspace.py`
- `src/onec_formbin/cli.py` for `inspect`, `unpack`, `pack`, or `roundtrip-check`

Out of scope:
- AST parsing or AST-backed diff rendering;
- semantic understanding of ordinary-form concepts;
- adding support claims for undocumented container variants without fixture evidence;
- changing fixture files as part of tuning.

# Raw-First Guard

Protect the repository's main feature: parsing 1C ordinary-form `Form.bin`
files through the raw-first workflow in `onec-formbin`.

This managed feature pack covers:
- deterministic container parsing and record exposure through `inspect`;
- unpacking `Form.bin` into a lossless raw-first workspace and packing it back;
- roundtrip behavior, mirror/preserve size-policy enforcement, and CLI workflow;
- diff and experimental AST behavior within the current verified support boundary.

Use this pack by default for general product work, especially when a change
touches more than one slice or when it is not obvious up front whether the risk
is in container parsing, diff, or the AST path.

Typical touch points:
- `src/onec_formbin/container.py`
- `src/onec_formbin/api.py`
- `src/onec_formbin/diffing.py`
- `src/onec_formbin/form_ast.py`
- CLI behavior that changes `inspect`, `unpack`, `pack`, `roundtrip-check`,
  `diff`, `parse-form`, or `build-form`

Out of scope:
- adding support claims for new undocumented container variants without fixtures;
- making the experimental AST layer mandatory for the raw-first codec;
- changing fixture files as part of tuning.

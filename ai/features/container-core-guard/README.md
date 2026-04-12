# Container Core Guard Pack

Use this feature pack for managed changes that affect the low-level raw-first
container codec.

What it protects:
- CLI behavior for `inspect`, `unpack`, `pack`, and `roundtrip-check`;
- byte-identical unpack/pack roundtrip for the managed fixture set;
- mirror versus preserve size-policy behavior during repack;
- pointer metadata exposure for split-form fixtures.

Split intent:
- `dev.jsonl`: fast checks on baseline fixtures and focused codec tests;
- `holdout.jsonl`: confirmation on the non-mirror split-form fixture after a
  candidate is kept.

Typical flow:
1. `make validate-feature FEATURE=container-core-guard`
2. `make feature-start FEATURE=container-core-guard`
3. `make feature-baseline FEATURE=container-core-guard RUN_ID=<run-id>`
4. Make one small reversible codec change.
5. `make feature-iteration FEATURE=container-core-guard RUN_ID=<run-id>`
6. `make feature-holdout FEATURE=container-core-guard RUN_ID=<run-id>`

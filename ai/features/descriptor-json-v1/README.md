# Descriptor JSON V1 Pack

Use this feature pack for structured decoding of descriptor records.

Current stage:
- `inspect --json` exposes an experimental `descriptor_json` block for known
  `form` and `module` descriptors;
- `semantic-form` carries the same decoded descriptor summary;
- the raw-first codec still treats descriptor bytes as lossless binary payload.

Target outcome:
- decode `form` and `module` descriptor records into stable JSON summaries;
- surface descriptor summaries in `inspect --json` and semantic-model exports;
- preserve lossless raw handling for unknown bytes.

Split intent:
- `dev.jsonl`: descriptor JSON guards on standard fixtures plus roundtrip safety;
- `holdout.jsonl`: confirmation on the split-form fixture after a candidate is kept.

Typical flow:
1. `make validate-feature FEATURE=descriptor-json-v1`
2. `make feature-start FEATURE=descriptor-json-v1`
3. `make feature-baseline FEATURE=descriptor-json-v1 RUN_ID=<run-id>`
4. Tighten descriptor JSON shape in small reversible steps.
5. Keep raw-first repack green while descriptor visibility improves.

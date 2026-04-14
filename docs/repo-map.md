# Repository Map

This repository is intentionally small. Use this document as the primary map
before reading code file-by-file.

## Top-level layout

- `src/onec_formbin/`: package source
- `tests/`: fixture-backed behavior tests
- `tests/fixtures/`: local `Form.bin` samples and support matrix
- `docs/adr/0001-raw-first.md`: accepted raw-first architecture decision
- `docs/workspace-contract.md`: source of truth for future workspace artifact names and schemas
- `docs/agent/`: repo-local onboarding and review router for managed feature work
- `automation/context/`: summary-first process map for agents
- `scripts/qa/`: onboarding and process integrity entrypoints
- `scripts/feature_loop.py`: eval-driven keep/revert runner
- `ai/features/`: managed feature packs and case manifests

## Main code paths

### CLI entry points

- `src/onec_formbin/cli.py`
- Commands:
  - `inspect` for `Form.bin` files and unpack dirs that contain `container.inspect.json`
  - `unpack`
  - `pack`
  - `roundtrip-check`
  - `diff`
  - `parse-form`
  - `build-form`
  - `semantic-form`
  - `apply-semantic`

Edit this file when the command surface, options, exit codes, or user-visible
messages change.

### Raw-first container workflow

- `src/onec_formbin/api.py`
- `src/onec_formbin/container.py`
- `src/onec_formbin/workspace.py`
- `src/onec_formbin/models.py`

Responsibilities:

- parse container bytes into records
- classify records conservatively
- unpack records into a manifest + `records/` tree
- repack while preserving unknown bytes and refusing unsafe size changes

Edit these files for container structure, manifest schema, record naming,
pointer handling, and repack safety policy.

### Diff workflow

- `src/onec_formbin/diffing.py`

Responsibilities:

- load either packed files or unpack directories
- compare metadata and payload bytes
- render raw, AST-backed, or semantic-slice diffs
- prefer materialized `semantic/*.json` workspace slices between unpack dirs
  when raw form bytes are unchanged

Edit this file when diff behavior, reporting, or form render modes change.

### Experimental AST workflow

- `src/onec_formbin/form_ast.py`

Responsibilities:

- parse `form.raw` brace syntax into a generic AST
- serialize AST back into brace text
- support split-form continuation records for known fixtures

This layer is intentionally separate from the main pack/unpack codec. Do not
make raw container safety depend on AST semantics.

### Experimental semantic-model workflow

- `src/onec_formbin/semantic_form.py`
- `src/onec_formbin/descriptor_json.py`

Responsibilities:

- build a stable semantic summary from a `Form.bin`, unpack dir, or `form.raw`;
- materialize the current semantic slices into `semantic/*.json` during unpack;
- materialize ordinary-form bundle support metadata into `support/*.json`
  during unpack and semantic refresh;
- apply the current narrow semantic write subset back to `records/*-form.raw`;
- reuse the inspect/container backbone when it is already available in an
  unpack workspace;
- decode known descriptor bodies into stable JSON summaries;
- combine container metadata with AST-derived structure summaries;
- stay explicitly narrower than full ordinary-form semantics.

This layer is a summary/export layer on top of the current parser. Do not claim
full semantic understanding unless new fixture-backed evidence exists.

The canonical target artifact names and slice boundaries for this layer live in
`docs/workspace-contract.md`.

## Change guidance

- If a change affects record parsing or repack policy, verify round-trip and
  size-policy behavior first.
- If a change affects CLI output or exits, verify the CLI directly in addition
  to running tests.
- If a change broadens support claims, update `README.md` and
  `tests/fixtures/README.md` together.
- If a change is driven through the eval loop, start from `docs/agent/index.md`
  and use the repo-owned `Makefile` targets instead of ad hoc commands.

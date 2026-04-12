# Architecture Map

`onec-formbin` now exposes a thin eval-driven process layer on top of its
existing repo docs.

## Process Surfaces

- `AGENTS.md`: repo-level rules and the preferred router.
- `docs/repo-map.md`: source-tree map for product code.
- `docs/verification.md`: real repo verification commands.
- `code_review.md`: raw-first review rules.
- `docs/agent/`: process-layer router for managed feature work.
- `automation/context/`: summary-first shortcuts for agents.
- `scripts/qa/`: onboarding and process integrity entrypoints.
- `scripts/feature_loop.py`: the public loop CLI.
- `scripts/feature_loop_core.py`: reusable loop logic including audit and clean replay.
- `scripts/feature_loop_adapter.py`: optional adapter for `input -> expected` cases.
- `scripts/feature_resume.py`: latest-run discovery for continuation after a new session.
- `ai/features/<feature-id>/`: feature contracts, constraints, scorecards, and case manifests.

## Behavioral Contract

- Product behavior is still verified by the repo's real checks from
  `docs/verification.md`.
- Managed feature work should use repo-owned entrypoints from `Makefile`,
  `scripts/qa/`, and `ai/features/` instead of one-off shell improvisation.
- New sessions should resume an existing run through `make feature-resume`
  before creating a new one.
- Development evidence comes from dev checks and manifests.
- Holdout evidence is reserved for confirmation.
- The process layer stays thin: it routes work, but it does not replace the
  repo's existing docs, fixtures, or raw-first constraints.

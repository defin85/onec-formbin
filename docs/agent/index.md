# Agent Docs Index

This directory is the agent-facing router for the eval-driven process layer in
`onec-formbin`.

## Quick Route

1. Read [AGENTS.md](../../AGENTS.md).
2. Read [docs/repo-map.md](../repo-map.md) for the code layout.
3. Read [docs/verification.md](../verification.md) for the repo's real checks.
4. Read [docs/agent/architecture.md](architecture.md) for the process surface.
5. Run the first safe verification path from [docs/agent/verify.md](verify.md).
6. Resume the default product run with `make feature-resume FEATURE=raw-first-guard`.

## Authoritative Map

| Question | File |
| --- | --- |
| Where should onboarding start? | [AGENTS.md](../../AGENTS.md) |
| What does this repo do? | [README.md](../../README.md) |
| Where is the code layout documented? | [docs/repo-map.md](../repo-map.md) |
| Where is the repo's real verification guide? | [docs/verification.md](../verification.md) |
| What process surfaces are installed in this repo? | [docs/agent/architecture.md](architecture.md) |
| What is the first safe verification path? | [docs/agent/verify.md](verify.md) |
| How should feature work be reviewed? | [docs/agent/review.md](review.md), [code_review.md](../../code_review.md) |
| What is the curated repo map? | [automation/context/project-map.md](../../automation/context/project-map.md) |
| What is the summary-first context layer? | [automation/context/hotspots-summary.generated.md](../../automation/context/hotspots-summary.generated.md) |
| Which skills or workflows are relevant in the first hour? | [automation/context/recommended-skills.generated.md](../../automation/context/recommended-skills.generated.md) |
| Where are feature packs stored? | [ai/features/README.md](../../ai/features/README.md) |
| How should the latest autoresearch run be resumed? | [docs/agent/verify.md](verify.md) |
| What is the read-only onboarding command? | `make codex-onboard` |
| What is the baseline verification command? | `make agent-verify` |

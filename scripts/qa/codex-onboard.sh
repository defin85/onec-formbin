#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"

printf '# Codex Onboard\n\n'
printf 'Canonical onboarding router: docs/agent/index.md\n'
printf 'Code layout: docs/repo-map.md\n'
printf 'Verification guide: docs/verification.md\n'
printf 'Project map: automation/context/project-map.md\n'
printf 'Summary-first map: automation/context/hotspots-summary.generated.md\n'
printf 'Recommended skills: automation/context/recommended-skills.generated.md\n'
printf 'Verification entrypoint: make agent-verify\n'
printf 'Feature pack root: ai/features/\n'

printf '\nAvailable feature packs:\n'
found=0
while IFS= read -r feature_dir; do
  feature_name="$(basename "$feature_dir")"
  if [ "$feature_name" = "TEMPLATE" ]; then
    continue
  fi
  found=1
  printf -- '- %s\n' "$feature_name"
done < <(find "$ROOT/ai/features" -mindepth 1 -maxdepth 1 -type d | LC_ALL=C sort)

if [ "$found" -eq 0 ]; then
  printf -- '- none detected\n'
fi

cat <<'EOF'

Next commands:
- make agent-verify
- make feature-resume [FEATURE=<feature-id>]
- make validate-feature FEATURE=<feature-id>
- make feature-start FEATURE=<feature-id>
- make feature-baseline FEATURE=<feature-id> RUN_ID=<run-id>
- make feature-iteration FEATURE=<feature-id> RUN_ID=<run-id>
- make feature-holdout FEATURE=<feature-id> RUN_ID=<run-id>
- make feature-ci-replay RUN_ID=<run-id> [PHASE=both]
EOF

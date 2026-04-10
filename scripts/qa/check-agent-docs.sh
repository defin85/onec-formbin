#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
PYTHON_BIN="${PYTHON:-python3}"
status=0

require_path() {
  local rel="$1"
  if [ ! -e "$ROOT/$rel" ]; then
    printf 'missing required path: %s\n' "$rel" >&2
    status=1
  fi
}

require_executable() {
  local rel="$1"
  if [ ! -x "$ROOT/$rel" ]; then
    printf 'missing executable bit: %s\n' "$rel" >&2
    status=1
  fi
}

require_path AGENTS.md
require_path Makefile
require_path README.md
require_path docs/repo-map.md
require_path docs/verification.md
require_path code_review.md
require_path docs/agent/index.md
require_path docs/agent/architecture.md
require_path docs/agent/verify.md
require_path docs/agent/review.md
require_path automation/context/project-map.md
require_path automation/context/hotspots-summary.generated.md
require_path automation/context/recommended-skills.generated.md
require_path ai/features/README.md
require_path scripts/feature_loop.py
require_path scripts/feature_loop_core.py
require_path scripts/feature_loop_adapter.py
require_path scripts/start_run.py
require_path scripts/validate_dataset.py
require_path scripts/qa/codex-onboard.sh
require_path scripts/qa/agent-verify.sh
require_path scripts/qa/check-agent-docs.sh

require_executable scripts/qa/codex-onboard.sh
require_executable scripts/qa/agent-verify.sh
require_executable scripts/qa/check-agent-docs.sh

"$PYTHON_BIN" - "$ROOT" <<'PY'
from __future__ import annotations

import re
import sys
from pathlib import Path


root = Path(sys.argv[1])
status = 0
markdown_files = [
    root / "AGENTS.md",
    root / "README.md",
    root / "docs" / "repo-map.md",
    root / "docs" / "verification.md",
    root / "code_review.md",
    root / "docs" / "agent" / "index.md",
    root / "docs" / "agent" / "architecture.md",
    root / "docs" / "agent" / "verify.md",
    root / "docs" / "agent" / "review.md",
    root / "automation" / "context" / "project-map.md",
    root / "automation" / "context" / "hotspots-summary.generated.md",
    root / "automation" / "context" / "recommended-skills.generated.md",
    root / "ai" / "features" / "README.md",
]
pattern = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def normalize_anchor(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[`\"]", "", value)
    value = re.sub(r"\s+", "-", value)
    value = re.sub(r"[^a-z0-9._-]", "", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value


def anchor_exists(path: Path, anchor: str) -> bool:
    wanted = normalize_anchor(anchor)
    if not wanted:
        return False
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("#"):
            continue
        heading = re.sub(r"^#{1,6}\s+", "", line)
        if normalize_anchor(heading) == wanted:
            return True
    return False


for file_path in markdown_files:
    text = file_path.read_text(encoding="utf-8")
    for match in pattern.finditer(text):
        target = match.group(1)
        if target.startswith(("http://", "https://", "mailto:", "tel:")):
            continue
        target_path = target
        anchor = ""
        if "#" in target:
            target_path, anchor = target.split("#", 1)
        resolved = file_path if not target_path else (file_path.parent / target_path).resolve()
        try:
            resolved.relative_to(root.resolve())
        except ValueError:
            print(f"link escapes repo root: {file_path.relative_to(root)} -> {target}", file=sys.stderr)
            status = 1
            continue
        if not resolved.exists():
            print(f"broken markdown link: {file_path.relative_to(root)} -> {target}", file=sys.stderr)
            status = 1
            continue
        if anchor and resolved.is_file() and not anchor_exists(resolved, anchor):
            print(f"missing markdown anchor: {file_path.relative_to(root)} -> {target}", file=sys.stderr)
            status = 1

if status:
    raise SystemExit(status)
PY

while IFS= read -r feature_dir; do
  [ -n "$feature_dir" ] || continue
  require_path "${feature_dir#"$ROOT/"}"/feature.md
  require_path "${feature_dir#"$ROOT/"}"/change-constraints.md
  require_path "${feature_dir#"$ROOT/"}"/checklist.md
  require_path "${feature_dir#"$ROOT/"}"/dev.jsonl
  require_path "${feature_dir#"$ROOT/"}"/holdout.jsonl
  "$PYTHON_BIN" "$ROOT/scripts/validate_dataset.py" \
    --dev "${feature_dir#"$ROOT/"}"/dev.jsonl \
    --holdout "${feature_dir#"$ROOT/"}"/holdout.jsonl >/dev/null || status=1
done < <(find "$ROOT/ai/features" -mindepth 1 -maxdepth 1 -type d | LC_ALL=C sort)

if [ "$status" -ne 0 ]; then
  exit "$status"
fi

printf 'Agent-facing docs check passed\n'

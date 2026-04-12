from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNS_DIR = ROOT / "logs" / "runs"
DEFAULT_FEATURE = "raw-first-guard"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Show the latest autoresearch run for a feature and how to continue it."
    )
    parser.add_argument(
        "--feature",
        default=DEFAULT_FEATURE,
        help=f"Feature id under ai/features/ (default: {DEFAULT_FEATURE}).",
    )
    parser.add_argument(
        "--fail-if-exists",
        action="store_true",
        help="Exit non-zero when a prior run already exists for the feature.",
    )
    return parser.parse_args()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def find_latest_run(feature: str) -> tuple[Path, dict[str, Any], dict[str, Any] | None] | None:
    if not RUNS_DIR.exists():
        return None

    feature_dir = f"ai/features/{feature}"
    for run_dir in sorted((path for path in RUNS_DIR.iterdir() if path.is_dir()), reverse=True):
        metadata_path = run_dir / "metadata.json"
        if not metadata_path.exists():
            continue
        metadata = read_json(metadata_path)
        if metadata.get("feature_dir") != feature_dir and metadata.get("name") != feature:
            continue
        state_path = run_dir / "loop-state.json"
        state = read_json(state_path) if state_path.exists() else None
        return run_dir, metadata, state
    return None


def print_no_run(feature: str) -> None:
    print(f"Feature: {feature}")
    print("Status: no existing runs found")
    print("Next commands:")
    print(f"- make feature-start FEATURE={feature}")


def print_existing_run(
    feature: str, run_dir: Path, metadata: dict[str, Any], state: dict[str, Any] | None
) -> None:
    run_id = metadata.get("run_id", run_dir.name)
    print(f"Feature: {feature}")
    print(f"Latest run: {run_id}")
    print(f"Run dir: {relative(run_dir)}")
    print(f"Summary: {relative(run_dir / 'summary.md')}")

    if state is None:
        print("Status: run created, baseline pending")
        print("Next commands:")
        print(f"- make feature-baseline FEATURE={feature} RUN_ID={run_id}")
        return

    best = state["best_score"]
    print(
        "Best dev score: "
        f"{best['passed']}/{best['total']} ({best['ratio']:.1%}) "
        f"at iteration {state['best_iteration']}"
    )

    holdout = state.get("holdout")
    if holdout is None:
        print("Holdout: pending")
    else:
        score = holdout["score"]
        print(
            "Holdout: "
            f"{score['passed']}/{score['total']} ({score['ratio']:.1%}) "
            f"at iteration {holdout['iteration']}"
        )

    print("Next commands:")
    print(f"- make feature-iteration FEATURE={feature} RUN_ID={run_id}")
    print(f"- make feature-holdout FEATURE={feature} RUN_ID={run_id}")
    print(f"- make feature-ci-replay RUN_ID={run_id} PHASE=both")


def fail_existing_run(
    feature: str, run_dir: Path, metadata: dict[str, Any], state: dict[str, Any] | None
) -> int:
    run_id = metadata.get("run_id", run_dir.name)
    print(
        f"Refusing to start a new run for feature '{feature}': existing run found: {run_id}",
        file=sys.stderr,
    )
    print(f"Summary: {relative(run_dir / 'summary.md')}", file=sys.stderr)
    if state is None:
        print(
            f"Continue with: make feature-baseline FEATURE={feature} RUN_ID={run_id}",
            file=sys.stderr,
        )
    else:
        print(
            f"Continue with: make feature-iteration FEATURE={feature} RUN_ID={run_id}",
            file=sys.stderr,
        )
        print(
            f"Or confirm with: make feature-holdout FEATURE={feature} RUN_ID={run_id}",
            file=sys.stderr,
        )
    return 3


def main() -> int:
    args = parse_args()
    result = find_latest_run(args.feature)
    if result is None:
        print_no_run(args.feature)
        return 0

    run_dir, metadata, state = result
    if args.fail_if_exists:
        return fail_existing_run(args.feature, run_dir, metadata, state)
    print_existing_run(args.feature, run_dir, metadata, state)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

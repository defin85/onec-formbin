SHELL := bash
PYTHON ?= python3
UV ?= uv run

.PHONY: help codex-onboard agent-verify validate-feature feature-resume feature-start feature-baseline feature-iteration feature-holdout feature-revert feature-ci-replay

help:
	@printf '%s\n' \
		'Available targets:' \
		'  make codex-onboard' \
		'  make agent-verify' \
		'  make validate-feature FEATURE=<feature-id>' \
		'  make feature-resume [FEATURE=<feature-id>]' \
		'  make feature-start FEATURE=<feature-id>' \
		'  make feature-baseline FEATURE=<feature-id> RUN_ID=<run-id>' \
		'  make feature-iteration FEATURE=<feature-id> RUN_ID=<run-id>' \
		'  make feature-holdout FEATURE=<feature-id> RUN_ID=<run-id>' \
		'  make feature-revert RUN_ID=<run-id>' \
		'  make feature-ci-replay RUN_ID=<run-id> [PHASE=both]'

codex-onboard:
	@./scripts/qa/codex-onboard.sh

agent-verify:
	@./scripts/qa/agent-verify.sh

validate-feature:
	@test -n "$(FEATURE)" || { echo 'FEATURE is required'; exit 2; }
	@$(UV) python scripts/validate_dataset.py \
		--dev "ai/features/$(FEATURE)/dev.jsonl" \
		--holdout "ai/features/$(FEATURE)/holdout.jsonl"

feature-resume:
	@$(UV) python scripts/feature_resume.py --feature "$(or $(FEATURE),raw-first-guard)"

feature-start:
	@test -n "$(FEATURE)" || { echo 'FEATURE is required'; exit 2; }
	@$(UV) python scripts/feature_resume.py --feature "$(FEATURE)" --fail-if-exists
	@$(UV) python scripts/start_run.py --name "$(FEATURE)" --feature-dir "ai/features/$(FEATURE)"

feature-baseline:
	@test -n "$(FEATURE)" || { echo 'FEATURE is required'; exit 2; }
	@test -n "$(RUN_ID)" || { echo 'RUN_ID is required'; exit 2; }
	@$(UV) python scripts/feature_loop.py baseline \
		--run-id "$(RUN_ID)" \
		--dev "ai/features/$(FEATURE)/dev.jsonl" \
		--holdout "ai/features/$(FEATURE)/holdout.jsonl"

feature-iteration:
	@test -n "$(FEATURE)" || { echo 'FEATURE is required'; exit 2; }
	@test -n "$(RUN_ID)" || { echo 'RUN_ID is required'; exit 2; }
	@$(UV) python scripts/feature_loop.py iteration \
		--run-id "$(RUN_ID)" \
		--dev "ai/features/$(FEATURE)/dev.jsonl" \
		--holdout "ai/features/$(FEATURE)/holdout.jsonl" \
		--auto-revert

feature-holdout:
	@test -n "$(FEATURE)" || { echo 'FEATURE is required'; exit 2; }
	@test -n "$(RUN_ID)" || { echo 'RUN_ID is required'; exit 2; }
	@$(UV) python scripts/feature_loop.py holdout \
		--run-id "$(RUN_ID)" \
		--holdout "ai/features/$(FEATURE)/holdout.jsonl"

feature-revert:
	@test -n "$(RUN_ID)" || { echo 'RUN_ID is required'; exit 2; }
	@$(UV) python scripts/feature_loop.py revert --run-id "$(RUN_ID)" --verify

feature-ci-replay:
	@test -n "$(RUN_ID)" || { echo 'RUN_ID is required'; exit 2; }
	@$(UV) python scripts/feature_loop.py ci-replay \
		--run-id "$(RUN_ID)" \
		--phase "$(or $(PHASE),both)"

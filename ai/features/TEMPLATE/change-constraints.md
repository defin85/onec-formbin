# Feature Change Constraints

List the non-negotiable boundaries for this feature pack.

## Protected files

List files or directories the loop must not edit.

## API and schema invariants

List interfaces that must remain stable unless explicitly approved.

## Verification boundaries

- Do not edit holdout manifests during tuning.
- Do not weaken checks to inflate the score.
- Do not move examples from holdout into development after seeing holdout failures.

## Operational boundaries

List performance, safety, compliance, or rollout constraints that must not be violated.

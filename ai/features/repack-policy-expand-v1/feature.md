# Repack Policy Expand V1

Expand the set of safe repack cases while preserving the raw-first contract for
unknown or undocumented size semantics.

This roadmap feature is intended to evolve toward:
- additional fixture-backed size-changing edits that can be repacked safely;
- clearer policy boundaries for mirror versus preserve behavior;
- better evidence for when a size field can or cannot be recomputed.

Current scaffold state:
- the manifests currently guard the existing mirror-safe and preserve-refusal behavior;
- before claiming wider repack support, add fixtures that prove the new policy case.

Use this pack when a change touches:
- `src/onec_formbin/api.py`
- `src/onec_formbin/container.py`
- `src/onec_formbin/workspace.py`
- tests or docs that define repack policy

Out of scope:
- silently relaxing preserve-policy safeguards without evidence;
- claiming support for undocumented variants without fixtures;
- editing holdout fixtures during tuning.

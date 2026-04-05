# Code Review Guide

Review this repository with a raw-first, safety-first mindset.

## Must-hold invariants

- Preserve opaque bytes unless a change is explicitly justified and tested.
- Do not broaden support claims beyond verified fixtures.
- Keep the experimental AST layer independent from the core unpack/pack codec.
- Reject unsafe size-changing edits for records with undocumented non-mirrored
  size fields.

## Review checklist

- Does the change preserve no-op round-trip behavior?
- Does it keep pointer-record handling correct for known split-form fixtures?
- Are CLI exit codes and messages still documented accurately?
- Are `README.md`, `docs/verification.md`, and fixture notes updated when
  workflow or support changes?
- Is there a focused test update for behavior changes?

## High-risk areas

- `src/onec_formbin/container.py`
- `src/onec_formbin/api.py`
- `src/onec_formbin/diffing.py`
- `src/onec_formbin/form_ast.py`

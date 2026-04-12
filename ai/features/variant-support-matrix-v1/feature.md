# Variant Support Matrix V1

Introduce a disciplined support matrix for additional `Form.bin` variants while
preserving the current verified corpus and process boundaries.

This roadmap feature is intended to evolve toward:
- fixture-backed onboarding for new container variants;
- explicit support-matrix documentation for what the repo can and cannot handle;
- safer rollout of new variants through dev and holdout separation.

Current scaffold state:
- the manifests currently guard the existing three-fixture matrix and the docs
  that describe it;
- before claiming wider support, add new fixtures, matrix notes, and the
  matching manifest commands.

Use this pack when a change touches:
- `tests/fixtures/`
- `tests/fixtures/README.md`
- `README.md` support claims
- `docs/verification.md` or feature manifests that expand the verified corpus

Out of scope:
- claiming support for undocumented variants without fixture evidence;
- weakening holdout boundaries to reuse new fixtures everywhere;
- editing existing holdout fixtures during tuning.

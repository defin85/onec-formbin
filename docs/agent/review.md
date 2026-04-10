# Review Expectations

Review managed feature work against these questions first:

1. Does `ai/features/<feature-id>/feature.md` clearly match the implemented behavior?
2. Did the change stay inside `allowed_paths` and protected constraints?
3. Did the development score improve without weakening the harness?
4. Was holdout used only for confirmation?
5. Do the run logs explain why changes were kept or reverted?
6. Does the change still satisfy the raw-first invariants from [code_review.md](../../code_review.md)?
7. Were `README.md`, `docs/verification.md`, and fixture notes updated if support claims or workflow changed?

If any of those answers are unclear, the implementation is not ready to be called complete.

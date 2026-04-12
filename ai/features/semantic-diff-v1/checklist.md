# Checklist

- Does raw diff still report identical and changed inputs correctly on the managed fixtures?
- Does AST-backed diff remain stable while semantic diff is added?
- Does the new output move toward deterministic diffs of semantic workspace slices?
- Were semantic diff fixtures or expected outputs added before claiming semantic diff support?
- Does the implementation preserve the documented diff exit-code contract?
- Were docs updated if diff output or guarantees changed?

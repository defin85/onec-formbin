# Checklist

- Does the change keep AST rebuilds and mirror-safe edits working on the managed fixtures?
- Does the edit surface stay narrow enough for direct LLM edits on workspace slices?
- Do preserve-policy edits still fail safely on the holdout fixture?
- Were semantic-edit fixtures or expected outputs added before claiming edit support?
- Does the implementation keep semantic edits narrow, explicit, and optional?
- Were docs updated if edit guarantees or support claims changed?

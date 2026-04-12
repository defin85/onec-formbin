# Checklist

- Does `parse-form` still produce stable AST JSON for the managed fixture set?
- Does `build-form` preserve AST structure when reparsed through `parse-form`?
- Does `formbin diff --form-mode ast` still report AST-rendered differences correctly?
- Does split-form continuation handling still work when parsing from a `Form.bin`
  file and an unpack root directory?
- Were docs updated if AST guarantees, workflow, or support claims changed?

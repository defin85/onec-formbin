# Checklist

- Does the change still parse `Form.bin` into the expected raw-first records and
  editable artifacts on the managed fixtures?
- Do no-op roundtrip and mirror/preserve size-policy behavior still hold where
  required?
- Do the end-to-end CLI routes for `inspect`, `unpack`, `pack`,
  `roundtrip-check`, `diff`, and the experimental AST entrypoints remain within
  the current verified support boundary?
- Does the split-form preserve-policy fixture still confirm the holdout-only
  behavior?
- Were docs updated if verification flow or support claims changed?

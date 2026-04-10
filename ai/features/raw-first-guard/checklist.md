# Checklist

- Does the change preserve no-op roundtrip behavior for the known corpus?
- Does the change keep unsafe size-changing edits rejected when required?
- Does CLI smoke still succeed on the baseline fixture?
- Does diff and AST behavior remain within the current verified support boundary?
- Were docs updated if verification flow or support claims changed?

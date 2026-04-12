# Checklist

- Does `inspect --json` expose `descriptor_json` for known `form` and `module` descriptors?
- Does `semantic-form` carry the same decoded descriptor summary?
- Do unknown descriptor bodies still fall back to opaque, lossless reporting?
- Does unpack/pack remain byte-identical while descriptor JSON support is added?
- Were docs updated where descriptor JSON is now user-visible?

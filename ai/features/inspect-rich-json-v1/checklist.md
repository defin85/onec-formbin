# Checklist

- Does `inspect --json` stay valid on the managed fixtures while new fields are added?
- Does the richer output move toward a reusable `container.inspect.json` backbone?
- Are pointer and size-policy details still correct on the split-form holdout fixture?
- Were JSON assertions or goldens added before claiming richer inspect support?
- Does the implementation avoid coupling inspect richness to repack safety?
- Were docs updated if inspect output or guarantees changed?

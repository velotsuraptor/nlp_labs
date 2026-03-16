# Dataset Card — Lab5 update

## Splits & leakage
- Split strategy: stratified_random (seed=42), sizes train/val/test = 800/100/100.
- Exact duplicate leakage: train∩test=0, train∩val=2, val∩test=0.
- Near-duplicate leakage (cos>=0.95): train-test=1, train-val=2.
- Template leakage rows detected: 0; fit-only-on-train discipline: True.

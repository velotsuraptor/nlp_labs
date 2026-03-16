# Audit summary — Lab5

- strategy=stratified_random, seed=42, split=train/val/test=800/100/100
- exact_dup: train∩test=0, train∩val=2, val∩test=0
- near_dup(>=0.95): train-test=1, train-val=2
- template_leak_rows=0
- fit_only_train=True
- deterministic_split=True

# Final Audit Summary

## Project

Classical POS Tagging and Morphological Tagging for Ukrainian using UD Ukrainian-IU.

## Data

- Source: UD Ukrainian-IU (official UD treebank).
- Processed size in this project:
  - Sentences: 7092
  - Tokens: 122750
  - Splits (sentences): train 5521 / dev 673 / test 898
  - Splits (tokens): train 92927 / dev 12606 / test 17217

## Main Task

- Primary: UPOS sequence labeling.
- Extension: joint UPOS+FEATS.

## Models

- Majority baseline.
- Lexicon baseline (word -> most frequent label, with fallback).
- CRF sequence model with contextual token features.

## Final UPOS Results

- Lexicon baseline (test):
  - Accuracy: 0.8238
  - Macro-F1: 0.7358
- CRF (test):
  - Accuracy: 0.9549
  - Macro-F1: 0.8685
- CRF (dev):
  - Macro-F1: 0.8624

## Reliability and Validation

- JSON schema validation: implemented (`src/validate_output.py`).
- Regression pack: 20/20 valid cases (`tests/run_regression.py`).
- Fallback path verified: baseline prediction when main model fails.
- Trace logging available: `outputs/pipeline_trace_upos.json`.

## Key Error Patterns

Top confusion pairs from test error cases:
- ADJ -> NOUN
- NOUN -> PROPN
- NOUN -> ADJ
- ADJ -> PROPN
- PART -> CCONJ

## Known Limitation

Joint CRF (UPOS+FEATS) training is runtime-heavy in the current environment and did not complete within available timeouts.

## Reproducibility

See `README.md` for setup and run commands:
1. `python -m src.load_data`
2. `python -m src.preprocess`
3. `python -m src.train_baselines --label-field upos`
4. `python -m src.train_crf --label-field upos`
5. `python -m src.predict ...`
6. `python -m src.validate_output ...`
7. `python tests/run_regression.py ...`

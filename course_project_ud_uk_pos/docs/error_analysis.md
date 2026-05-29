# Error Analysis Plan

## Goals

- Identify the most frequent systematic POS errors
- Compare baseline errors against CRF errors
- Separate lexical sparsity issues from contextual ambiguity
- Inspect whether joint `UPOS + FEATS` labels fail due to the POS decision or the morphology bundle

## Main Slices

- OOV vs in-vocabulary tokens
- Short vs long sentences
- Frequent vs rare labels
- Proper names
- Numerals
- Punctuation-adjacent tokens
- Hyphenated tokens
- Apostrophe-containing tokens

## Concrete Outputs

- `outputs/error_cases_*.jsonl`
- top confusion pairs
- per-label F1
- sentence-level exact-match accuracy

## Five Errors To Show In Final Demo

1. `NOUN` vs `PROPN`
2. `DET` vs `PRON`
3. `ADV` vs `PART`
4. rare morphology bundle unseen in train
5. OOV token with misleading suffix


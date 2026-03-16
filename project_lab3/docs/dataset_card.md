# Dataset Card — Lab3 update

## Data source
- Input: Lab2 processed_v2.csv (UAReviews subset, N=1000).

## Added linguistic features
- lemma_text from Stanza
- upos_seq (UPOS tag sequence)

## Baseline effect
- processed_v2 macro-F1: 0.6260
- lemma_text macro-F1: 0.7031
- text+POS macro-F1: 0.6159
- delta lemma vs text: +0.0772
- delta text+POS vs text: -0.0101

## Decision
- Use lemma_text as default classical baseline in next labs.
- Keep POS features optional and validate per-task.

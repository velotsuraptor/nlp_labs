# Audit summary — Lab3 (Lemma/POS baseline)

## Metrics

- processed_v2: acc=0.6250, macroF1=0.6260
- lemma_text: acc=0.7050, macroF1=0.7031
- text+POS: acc=0.6150, macroF1=0.6159

## Decision

- Lemma baseline changed macro-F1 by +0.0772 vs processed_v2.
- Text+POS changed macro-F1 by -0.0101 vs processed_v2.
- For this corpus, lemma features reduce lexical sparsity and improve generalization.
- POS n-grams alone add limited signal and may introduce sparsity/noise for short reviews.
- Recommended default: use lemma_text for classical ML baseline and keep POS as optional feature.

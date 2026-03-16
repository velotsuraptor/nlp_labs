# LPNU NLP — Lab 03 (Lemma/POS baseline, UA)

## 1) Track
A — text classification (UAReviews categories).

## 2) Lemma/POS tool
Stanza (Ukrainian tokenize+POS+lemma).

## 3) Baselines compared
- Baseline 1: TF-IDF + Linear SVM on processed_v2 text
- Baseline 2: TF-IDF + Linear SVM on lemma_text
- Baseline 3: TF-IDF(text) + TF-IDF(POS n-grams) + Linear SVM

Metrics: accuracy + macro-F1.

## 4) Key results
- processed_v2: acc=0.6250, macro-F1=0.6260
- lemma_text: acc=0.7050, macro-F1=0.7031
- +POS: acc=0.6150, macro-F1=0.6159

## 5) Decision
- Lemma baseline changed macro-F1 by +0.0772 vs processed_v2.
- Text+POS changed macro-F1 by -0.0101 vs processed_v2.
- For this corpus, lemma features reduce lexical sparsity and improve generalization.
- POS n-grams alone add limited signal and may introduce sparsity/noise for short reviews.
- Recommended default: use lemma_text for classical ML baseline and keep POS as optional feature.

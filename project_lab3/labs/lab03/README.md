# LPNU NLP — Lab 03 (Lemma/POS baseline, UA)

## 1) Track
A — text classification (UAReviews categories).

## 2) Lemma/POS tool
Stanza (Ukrainian tokenize+POS+lemma).

## 3) Baselines compared
- Baseline 1: TF-IDF + Linear SVM on processed_v2 text
- Baseline 2: TF-IDF + Linear SVM on lemma_text
(Optional) Baseline 3: TF-IDF(text) + TF-IDF(POS n-grams)

Metrics: accuracy + macro-F1.

## 4) Key results
(заповнюється після запуску ноутбука)
- processed_v2: acc=__, macro-F1=__
- lemma_text: acc=__, macro-F1=__
- +POS: acc=__, macro-F1=__

## 5) Decision
Коротко: використовуємо леми/POS чи ні, і де саме.

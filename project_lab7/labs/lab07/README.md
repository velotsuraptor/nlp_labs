# LPNU NLP — Lab 07 (Linear SVM + char-ngrams + imbalance)

1. Task: compare Lab6 LogReg baseline against LinearSVC variants on the same fixed split.
2. Lab6 baseline reused: TF-IDF word(1,2) + Logistic Regression.
3. SVM variants: word(1,2), word+char(3,5), and word+char with class_weight="balanced".
4. Imbalance note: dataset is balanced overall, so class_weight effect is expected to be small.
5. PR/threshold section: one-vs-rest analysis for Complaint / Dissatisfaction using validation scores.
6. Error analysis shows overlap classes, rare vocabulary, and noisy/translit texts as the main issues.
7. Best model: svm_word_char (val macro-F1=0.6512, test macro-F1=0.7355).

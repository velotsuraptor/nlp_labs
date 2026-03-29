# Audit summary — Lab7

1. Track A multi-class classification on UAReviews categories.
2. Split: reused Lab5 train/val/test = 800/100/100, seed=42.
3. Lab6 baseline (LogReg word(1,2)): accuracy=0.6800, macro-F1=0.6786.
4. Best SVM variant (svm_word_char): accuracy=0.7400, macro-F1=0.7355.
5. Char-ngrams effect: svm_word_char test macro-F1=0.7355; balanced variant test macro-F1=0.7355.
6. class_weight=balanced effect: val macro-F1=0.6512 vs unbalanced 0.6512.
7. Top error categories: rare vocabulary, overlap класів, translit / slang / noisy text.
8. Next fixes: dedup/near-dup cleanup, char-ngram tuning, review borderline labels.

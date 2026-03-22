# Audit summary — Lab6

1) Підзадача: multi-class classification (Track A) для категорій повідомлень UAReviews.
2) Split: використано Lab5 split train/val/test = 800/100/100, seed=42.
3) Baseline 1 (baseline_1_word_1_1): accuracy=0.6800, macro-F1=0.6786 (test).
4) Baseline 2 (baseline_2_word_1_2): accuracy=0.6800, macro-F1=0.6786 (test).
5) Winner: baseline_2_word_1_2 (val macro-F1=0.5741); delta vs other on test macro-F1 = +0.0000.
6) Топ-3 категорії помилок: рідкісна лексика / неоднозначність, overlap: питання + скарга, overlap класів / змішаний намір.
7) Далі: дедуп/near-dup фільтрація, розширення n-gram/char-features, ревізія прикордонних label-пар.

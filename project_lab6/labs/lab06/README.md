# LPNU NLP — Lab 06 (TF-IDF + Logistic baseline)

1. Напрям: A (класифікація).
2. Підзадача: класифікація українських текстів UAReviews на 5 категорій.
3. Порівняні baseline-и: baseline_1_word_1_1 та baseline_2_word_1_2.
4. Основні цифри (test): baseline_1_word_1_1 acc=0.6800, macro-F1=0.6786; baseline_2_word_1_2 acc=0.6800, macro-F1=0.6786.
5. Error analysis: найчастіше трапляються overlap класів, короткі тексти та noisy/translit кейси; далі варто покращити розмітку прикордонних випадків і додати більш стійкі фічі.

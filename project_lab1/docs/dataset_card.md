# Назва проєкту
UAReviews Category Classification (Lab1)

## Задача
A) Класифікація текстів.
Input: український текст (відгук/коментар).
Output: один із 5 класів категорії повідомлення.

## Джерело даних
UAReviews (HuggingFace Datasets), завантаження через `datasets.load_dataset("KSE-RESEARCH-Group/UAReviews")`.
Посилання:
https://huggingface.co/datasets/KSE-RESEARCH-Group/UAReviews

## Обсяг
N = 1000 текстів (стратифікована вибірка).
Класів = 5 (по 200 прикладів на клас):
- Gratitude / Positive Feedback
- Complaint / Dissatisfaction
- Question / Request for Help
- Neutral Comment
- Suggestion / Idea

## Мова / домен
UA. Короткі відгуки/коментарі з різних джерел (поле `source` у датасеті).

## Очищення (processed.csv)
- прибрано зайві пробіли та переноси;
- уніфіковано апострофи до `'`;
- замінено URL/email/phone на `<URL>`, `<EMAIL>`, `<PHONE>` (regex).

## Перевірки якості (Lab1)
- точні дублі: 0.40%;
- дуже короткі (<5 слів): 0.20%;
- сміттєві рядки (лише цифри/символи): 0.00%.

## Ризики
- шум (помилки, сленг, розмітка в стилі соцмереж);
- можливі залишки контактних даних у тексті (маскування);
- доменний зсув (узагальнення на інші типи текстів не гарантоване).

## План Lab2
- видалити точні дублі після нормалізації;
- уточнити правила для прикордонних випадків між класами;
- підготувати baseline (наприклад, TF-IDF + Logistic Regression / Linear SVM).

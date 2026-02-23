# LPNU NLP — Lab 02 (Cleaning & Normalization Pipeline)

## 1) Track / Task
Track A (text classification). Поле `text` — українські відгуки/коментарі з UAReviews (Lab1 subset).

## 2) Colab запуск (2 кроки)
1) `pip install -r requirements.txt`
2) Відкрити `notebooks/lab2_cleaning_normalization.ipynb` і натиснути Run all (створить `data/processed_v2` та `docs/audit_summary_lab2.md`).

## 3) Правила очистки/нормалізації (коротко)
- whitespace/NBSP → один пробіл
- апострофи → `'`
- лапки → `"`
- тире/дефіси → `-`
- маскування URL/EMAIL/PHONE → `<URL>/<EMAIL>/<PHONE>`
- sentence split з захистом UA-скорочень (м., вул., р., т.д.) і чисел/версій (3.14, 1.2.3)

## 4) 5 найболючіших edge cases
- скорочення з крапкою (м., вул., т.д., тел.)
- десяткові числа та версії (3.14, 1.2.3)
- різні апострофи та лапки
- NBSP і множинні пробіли/переноси
- URL/EMAIL/PHONE у тексті

## 5) Що стало краще “після”
- менше шуму від різних пробілів/переносів
- стабільне маскування PII патернів
- sentence split менше “ламається” на скороченнях/числах
(конкретні цифри — в `docs/audit_summary_lab2.md`)

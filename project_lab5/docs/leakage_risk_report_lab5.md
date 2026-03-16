# Leakage risk report — Lab5

## 1) Стратегія split (яка і чому)
- Обрана стратегія: stratified random split 80/10/10 з фіксованим seed=42.
- Для нашого датасету (класифікація з 5 класами, N=1000) це дає стабільні частки класів у train/val/test.
- Ця стратегія запобігає перекосам класів, які могли б штучно покращити або погіршити метрики.
- Ми явно перевірили duplicate leakage між сплітами, щоб однакові тексти не потрапляли у train і test одночасно.
- Додатково перевірено near-duplicates через TF-IDF + cosine similarity (threshold=0.95).
- Пошук template leakage показує, чи немає службових підказок на кшталт label=/class=/topic= у тексті.
- Дисципліна fit-only-on-train зафіксована через sklearn Pipeline, де fit виконується тільки на train.

## 2) Статистика сплітів (розміри, баланс класів/джерел)
- Sizes: train=800, val=100, test=100, total=1000
- Complaint / Dissatisfaction: train=20.00%, val=20.00%, test=20.00%
- Gratitude / Positive Feedback: train=20.00%, val=20.00%, test=20.00%
- Neutral Comment: train=20.00%, val=20.00%, test=20.00%
- Question / Request for Help: train=20.00%, val=20.00%, test=20.00%
- Suggestion / Idea: train=20.00%, val=20.00%, test=20.00%
- source=original: train=97.25%, val=98.00%, test=99.00%
- source=cosmus: train=2.75%, val=2.00%, test=1.00%

## 3) Leakage checks results
- exact duplicates train∩test = 0
- exact duplicates train∩val = 2
- exact duplicates val∩test = 0
- near-duplicates train vs test (>=0.95): 1
- near-duplicates train vs val (>=0.95): 2
- template leakage rows: 0
- group overlap train/val=2, train/test=2, val/test=2
- time leakage: N/A (немає date-колонки)
- fit only on train: True

### 5 прикладів near-duplicate пар
- 12979 vs 13101 (cos=1.0000)
- 12886 vs 13195 (cos=1.0000)
- 15892 vs 15885 (cos=1.0000)

## 4) Ризики, що залишились
- Можливі семантично близькі пари з cosine < 0.95 (не покриті цим порогом).
- Group leakage не може бути повністю оцінений без author/user/thread ідентифікаторів.
- У текстах можуть лишатися доменні шаблони, які не збігаються з regex-патернами template leakage.

## 5) Що зробимо далі
- Додати MinHash/SimHash для більш чутливого near-duplicate аналізу.
- Якщо з'явиться user/thread/date, перейти на group/time-based split і повторити checks.
- Використовувати цей split manifest як фіксовану основу для Lab7-Lab8 метрик.

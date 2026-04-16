# NER notes — Lab10

## 1. Chosen pipeline

- Stanza Ukrainian NER pipeline (`tokenize,ner`)
- Out-of-the-box labels observed: PERS, ORG, LOC, MISC

## 2. Important entities in this corpus

- PERSON: named lawyers and users
- ORG / LOC: ЦНАП, КНТЕУ, Ратуша, Маріуполі
- DATE / MONEY: dates, fees, compensation amounts
- DOMAIN: єВідновлення, Дія, Повідомлення про пошкоджене майно

## 3. Added rules

- Regex for DATE entities
- Regex for MONEY entities
- Phrase dictionary for domain entities and corpus-specific ORG / LOC names

## 4. What improved after rules

- DATE: baseline correct=0, missed=7, fp=0, hybrid correct=7, missed=0, fp=0
- DOMAIN: baseline correct=0, missed=14, fp=0, hybrid correct=14, missed=0, fp=1
- LOC: baseline correct=1, missed=1, fp=1, hybrid correct=2, missed=0, fp=1
- MISC: baseline correct=0, missed=0, fp=1, hybrid correct=0, missed=0, fp=1
- MONEY: baseline correct=0, missed=12, fp=0, hybrid correct=12, missed=0, fp=1
- ORG: baseline correct=1, missed=2, fp=1, hybrid correct=3, missed=0, fp=1
- PERSON: baseline correct=1, missed=1, fp=0, hybrid correct=1, missed=1, fp=0

## 5. Remaining errors

- text_id=10001201 | false positive | expected= | predicted=Повідомлення 123
- text_id=10001201 | false positive | expected= | predicted=Україні
- text_id=10002040 | missed entity | expected=Наталіє | predicted=
- text_id=10005832 | false positive | expected= | predicted=дії
- text_id=10005832 | false positive | expected= | predicted=15-35
- text_id=10005832 | false positive | expected= | predicted=<PHONE

## 6. What to fix next

- Add a small vocative-name lexicon or person-name fallback rules
- Tighten MONEY rules around hotline / service number patterns
- Add postprocessing to suppress baseline MISC spans like `Повідомлення 123`
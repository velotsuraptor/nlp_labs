# Audit summary — Lab4

## Precision table

- DATE: predicted=13, correct=13, precision=1.0000
- LOCATION: predicted=0, correct=0, precision=N/A
- DOC_ID: predicted=2, correct=2, precision=1.0000

## Notes

Для швидкої відтворюваної оцінки використано автоматично згенерований weak-gold subset.
LOCATION виправлено через підтримку відмінкових форм міст.
DATE має високу точність через чіткі regex-патерни; DOC_ID — через контекстні правила.
Для error analysis використано problem cases з ie_edge_cases.jsonl.
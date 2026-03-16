# Audit summary — Lab4

## Precision table (edge-case based)

- DATE: predicted=4, correct=4, precision=1.0000, recall=1.0000, skipped_ambiguous=0
- LOCATION: predicted=5, correct=5, precision=1.0000, recall=1.0000, skipped_ambiguous=1
- DOC_ID: predicted=7, correct=7, precision=1.0000, recall=1.0000, skipped_ambiguous=1

## Notes

Оцінка зроблена на ie_edge_cases.jsonl (не на self-generated weak-gold).
Weak-gold збережено як допоміжний набір прикладів, але не як незалежний тест.
Precision-first anti-rules зменшують хибні DOC_ID/DATE спрацювання.

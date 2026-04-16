# Audit summary — Lab10

1. Pipeline used: Stanza Ukrainian NER (`tokenize,ner`).
2. Important entity types for this corpus: PERSON, ORG, LOC, DATE, MONEY, and domain entities such as `єВідновлення` / `Дія`.
3. Baseline strengths: it already catches some PERSON / ORG / LOC entities.
4. Baseline misses: almost all DATE, MONEY, and corpus-specific domain entities.
5. Added rules: date regex, money regex, and phrase-dictionary rules for domain entities / ORG / LOC.
6. What improved: baseline correct=3, missed=37, false_positive=3; hybrid correct=39, missed=1, false_positive=5.
7. Most frequent error categories: baseline mainly missed entity / missed domain entity; hybrid mainly false positives plus one remaining PERSON miss.
8. Next steps: better PERSON coverage for vocative forms, tighter filtering for hotline-like numbers, and stronger conflict resolution for baseline MISC spans.

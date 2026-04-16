# LPNU NLP — Lab 10 (NER pipeline + hybrid rules)

1. Evaluation set: 20 short documents from the cleaned `processed_v2` corpus with manual expected entities.
2. Pipeline: Stanza Ukrainian NER (`tokenize,ner`).
3. Added rules: DATE regex, MONEY regex, phrase dictionary for domain entities / ORG / LOC.
4. Baseline strengths: some PERSON / ORG / LOC detection.
5. Baseline misses: most DATE, MONEY, and corpus-specific domain entities.
6. Hybrid gains: large recall improvement for DATE, MONEY, DOMAIN, and better ORG / LOC coverage.
7. Remaining issues: false positives from baseline spans, one missed PERSON case, and ambiguous hotline-like number patterns.

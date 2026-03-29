# Dataset Card — Lab7 update

## New findings
- Compared LogReg and LinearSVC on the same fixed split from Lab5.
- Checked whether char-ngrams help with noisy text, translit, and spelling variation.
- Checked class_weight=balanced and one-vs-rest threshold behavior for Complaint / Dissatisfaction.

## Risks
- overlap class boundaries remain the main source of confusion
- noisy text / translit still hurts lexical models
- precision/recall tradeoff depends on threshold choice for binary OvR use cases

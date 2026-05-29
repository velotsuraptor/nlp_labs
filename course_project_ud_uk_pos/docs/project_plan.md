# Project Plan

## Objective

Build a classical NLP system for Ukrainian POS tagging on `UD Ukrainian-IU`, with joint morphology tagging as an extension.

## Deliverables

- reproducible dataset download and conversion
- dataset card and statistics
- majority and lexicon baselines
- CRF sequence labeler
- metrics and confusion matrix
- JSON inference example
- error analysis artifacts

## Stages

1. Data ingestion and conversion from `CoNLL-U`
2. EDA, statistics, and documentation
3. Baselines and CRF training
4. Evaluation, error analysis, and demo output

## Risks

- class imbalance
- ambiguous function words
- OOV tokens
- morphology bundle sparsity
- simplistic tokenizer at inference time

## Mitigations

- report macro-F1, not only accuracy
- keep baseline comparisons honest
- evaluate both sequence and token-level performance
- save difficult examples for manual review


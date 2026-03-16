# Dataset Card — Lab4 update

## IE fields
- DATE
- LOCATION
- DOC_ID

## Privacy & masking
- Inputs come from processed_v2 with URL/EMAIL/PHONE masking from Lab2.
- Rule extraction works on masked text to reduce direct PII exposure.

## Precision-first policy
- Conservative anti-rules reduce false positives for DATE/DOC_ID.
- Ambiguous cases are tracked separately and excluded from strict precision.

## Current metrics (edge cases)
- DATE precision: 1.0000
- LOCATION precision: 1.0000
- DOC_ID precision: 1.0000

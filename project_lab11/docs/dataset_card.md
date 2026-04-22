# Dataset card

- Source corpus: cleaned `processed_v2` texts from Lab 2.
- Lab 11 structured extraction case: support/admin-service messages about compensation, documents, queues, and state-service access.
- Text field used in this repo: `text` column inside `processed_v2.csv` (this file is the processed output).
- The corpus contains both explicit and implicit field values; service names are often explicit, while issue type and document naming can be implicit.
- Hard cases: multiple services in one message, implicit service references, ambiguous money/date mentions, and noisy user phrasing.
- Viability: LLM extraction is viable only with schema-first validation; repair loop improves structural stability, but not every semantic ambiguity disappears.

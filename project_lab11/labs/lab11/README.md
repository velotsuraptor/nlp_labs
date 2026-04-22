# Lab 11

1. Extraction case: support/admin message -> structured service JSON.
2. Schema: primary service, all services mentioned, issue type, document type, amounts, date, and location.
3. Baseline prompt: single-shot JSON-only extraction prompt with controlled enums and null rules.
4. Validator: strict `json.loads` + `jsonschema` Draft 2020-12 validation.
5. Repair loop: max 2 attempts, using the broken output plus validation error to force valid JSON.
6. Raw valid JSON rate: 0.500; raw schema-valid rate: 0.300; post-repair schema-valid rate: 1.000.
7. Remaining issues: semantic ambiguity around implicit services, document normalization, and some over-predicted fields.

# Lab 11 audit summary

- Extraction case: support/admin message -> structured service JSON (7 fields)
- Evaluation set size: 20
- Raw valid JSON rate: 0.500
- Raw schema-valid JSON rate: 0.300
- Post-repair valid JSON rate: 1.000
- Schema-valid JSON rate: 1.000
- Average repairs per example: 0.700
- Repair needed rate: 0.700
- Repair failed rate: 0.000
- Most fragile fields: `issue_type`=7, `primary_service`=5, `services_mentioned`=4, `document_type`=4
- Most frequent error categories: `semantic_extraction_error`=19, `json_parse_error`=10, `missing_required_field`=2, `wrong_field_type`=2, `normalization_issue`=1
- Schema-first result: validator + repair loop materially improved structured-output reliability; semantic mistakes still remain on ambiguous fields.

- Provider used during this run: `mock`

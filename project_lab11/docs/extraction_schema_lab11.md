# Lab 11 extraction schema

- Extraction task: support/admin message -> structured state-service attributes
- Fields: `primary_service`, `services_mentioned`, `issue_type`, `document_type`, `amounts_uah`, `date_text`, `location_text`
- Required fields: all seven fields are required by schema; nullable fields use `null`, and `amounts_uah` uses `[]` when absent.

## JSON schema
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "SupportAdminExtraction",
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "primary_service": {
      "type": "string",
      "enum": [
        "єВідновлення",
        "Дія",
        "ЦНАП",
        "Паспортний сервіс",
        "Нотаріус",
        "Державний реєстр нерухомості",
        "Інша держпослуга",
        "unknown"
      ]
    },
    "services_mentioned": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": [
          "єВідновлення",
          "Дія",
          "ЦНАП",
          "Паспортний сервіс",
          "Нотаріус",
          "Державний реєстр нерухомості",
          "Інша держпослуга",
          "unknown"
        ]
      },
      "uniqueItems": true
    },
    "issue_type": {
      "type": "string",
      "enum": [
        "compensation_status",
        "application_submission",
        "document_requirement",
        "payment_or_amount",
        "registration_or_queue",
        "service_access_problem",
        "inheritance_or_notary",
        "consultation_or_advice",
        "other"
      ]
    },
    "document_type": {
      "type": [
        "string",
        "null"
      ]
    },
    "amounts_uah": {
      "type": "array",
      "items": {
        "type": "number",
        "minimum": 0
      }
    },
    "date_text": {
      "type": [
        "string",
        "null"
      ]
    },
    "location_text": {
      "type": [
        "string",
        "null"
      ]
    }
  },
  "required": [
    "primary_service",
    "services_mentioned",
    "issue_type",
    "document_type",
    "amounts_uah",
    "date_text",
    "location_text"
  ]
}
```

## Null / missing rules
- `document_type`, `date_text`, `location_text`: use `null` if the value is not explicit in the text.
- `amounts_uah`: use an empty array if no money amount is explicitly stated.

## Frequent problem fields
- `issue_type`=7, `primary_service`=5, `services_mentioned`=4, `document_type`=4

## What repair loop actually fixes
- Broken wrappers such as markdown fences / extra commentary around JSON.
- Missing required fields and wrong field types from the raw extraction output.
- It does not fully solve semantic ambiguity in service choice or normalized document naming.

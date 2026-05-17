# Lab 14 — Flow Notes

## 1. Use Case

Support extraction flow for Ukrainian admin-service messages. Users write in Ukrainian about issues with government digital services (Дія, єВідновлення, ЦНАП, Паспортний сервіс, Нотаріус). The flow classifies each message, extracts structured fields, validates the result, attempts repair if extraction fails, and exports a structured JSON record regardless of outcome. Built on the same domain as Lab 12 (schema-first extraction) but adds auditable stage tracking, explicit error handling, and a repair layer.

## 2. Stages

```
ingest → route → execute → validate → (fallback) → export
```

| Stage    | Input              | Output                          |
|----------|--------------------|---------------------------------|
| ingest   | raw text           | clean_text, status=ingested     |
| route    | clean_text         | route, schema_name, routing_reason |
| execute  | route, clean_text  | execute_output dict             |
| validate | execute_output     | validation_result dict          |
| fallback | clean_text + vr    | fallback_result dict (optional) |
| export   | full state         | structured export JSON          |

## 3. State Structure

`FlowState` is a dataclass with the following fields:

- `case_id` — unique identifier for the case
- `raw_text` — original unmodified input
- `clean_text` — text after normalization
- `route` — routing decision: `"support_extraction"` or `"manual_review"`
- `schema_name` — schema identifier associated with the route
- `routing_reason` — human-readable explanation of routing decision
- `execute_output` — dict of extracted fields (or None)
- `validation_result` — validation report dict (or None)
- `fallback_result` — repair outcome dict (or None)
- `final_output` — the cleaned export payload dict
- `status` — current pipeline status string
- `errors` — list of blocking error messages
- `warnings` — list of non-blocking warning messages
- `steps` — ordered list of stage-result dicts (audit trail)
- `fallback_triggered` — bool, True if fallback stage was activated

## 4. Possible Routes

**`support_extraction`** — default route when any meaningful signal is detected (service keyword, money amount, document keyword, or issue keyword). Uses `support_schema`. Required fields: `primary_service`, `issue_type`.

**`manual_review`** — triggered when input is empty, too short, or contains no known keywords. No extraction is attempted. Sets `fallback_triggered=True` and `status="safe_failure"` immediately.

## 5. Execute: Rule-Based Extraction

The executor runs rule-based detection in this order:

1. **Services**: scan lowercased text for trigger fragments corresponding to each of the 5 services. Detect ambiguity: if two or more services are found AND an ambiguity marker (`"чи"`, `"або"`) is present, set `primary_service = "unknown"`.
2. **Issue type**: match against ordered list of (issue_type, trigger_list) pairs; first match wins. Falls back to `"other"`.
3. **Document type**: regex scan for inflected forms of common document nouns.
4. **Amounts (UAH)**: regex `\d[\d\s]*\s*грн`.
5. **Dates**: regex covering numeric dates + relative words (завтра, сьогодні, вчора).
6. **Location**: string matching for known patterns (пл. Ринок, ЦНАП у [City]).
7. **Confidence**: `"high"` if both primary_service and issue_type resolved; `"medium"` if one resolved; `"low"` if neither.

## 6. Validate: Schema Check, Required Fields, Warnings

Validation checks in order:

- **Schema check**: all expected top-level keys are present in `execute_output`.
- **Required fields check**: `primary_service` and `issue_type` are non-empty.
- **Enum check**: `primary_service` in `SERVICE_ENUM`, `issue_type` in `ISSUE_ENUM`.
- **Warnings** (non-blocking):
  - `date_text` contains `"завтра"` — relative date
  - `primary_service == "unknown"` despite services detected — ambiguity
  - `primary_service == "unknown"` with no services — no signal
  - `confidence == "low"` — unreliable extraction
  - `confidence == "medium"` — review recommended
- **Recommended action**: `"accept"` / `"export_with_warning"` / `"fallback"` / `"safe_failure"`.

## 7. Fallback Triggers

Fallback is triggered by:

- `status == "validation_failed"` — required fields missing or enum violation
- `status == "execute_failed"` — execute raised an exception
- `route == "manual_review"` — router could not classify the text
- Empty input at ingest stage

Fallback attempts rule-based repair of `primary_service` (the most common failure). If exactly one service is found in the text during repair, `repaired_fields = {"primary_service": service}` and `action = "export_repaired"`. If repair fails, `action = "safe_failure"`.

## 8. Export Format

```json
{
  "case_id": "case_001_simple_service",
  "route": "support_extraction",
  "final_output": {
    "primary_service": "Дія",
    "services_mentioned": ["Дія", "єВідновлення"],
    "issue_type": "compensation_status",
    "document_type": "заяву",
    "amounts_uah": [],
    "date_text": null,
    "location_text": null
  },
  "status": "exported",
  "warnings": [],
  "errors": [],
  "needs_manual_review": false,
  "fallback_triggered": false
}
```

Internal fields (`execution_method`, `confidence`) are stripped before export. `needs_manual_review` is set to `True` when `fallback_triggered` is `True` or `status == "safe_failure"`.

## 9. What the Flow Improved Over Ad-Hoc Extraction

| Aspect                  | Ad-hoc (Lab 12 style)  | Flow (Lab 14)                   |
|-------------------------|------------------------|---------------------------------|
| Stage visibility        | None — black box       | `steps` list with per-stage status |
| Structured failure      | Exception or None      | `safe_failure` status + `errors` |
| Repair on failure       | None                   | Fallback stage with `repaired_fields` |
| Audit trail             | None                   | `FlowLogger` → JSONL            |
| Warnings surfaced       | Not systematically     | Explicit `warnings` list        |
| Export always produced  | No                     | Yes — even `safe_failure` yields a JSON record |

## 10. Where the Flow Was Redundant

For simple, clean cases (case_001, case_008, case_012) the flow adds 5 stages and state management overhead to what is essentially a single `execute()` call returning a dict. The routing step is also trivial for the current domain — all meaningful messages land in `support_extraction`. The multi-stage architecture pays off primarily for the 5 out of 12 cases where fallback or warning logic was needed.

## 11. Planned Improvements

1. **Repair for `issue_type`**: current fallback only repairs `primary_service`. Add a second repair pass using the same trigger-pattern lookup for issue type.
2. **Ambiguity scoring**: instead of a binary ambiguous/non-ambiguous flag, compute a confidence score based on the ratio of the strongest service match vs all service matches, allowing soft disambiguation.
3. **LLM-based fallback**: for cases where rule-based repair fails (currently 3/12 become `safe_failure`), add an optional LLM extraction call as a second-tier fallback.
4. **Timestamp-aware date resolution**: replace relative date warnings with actual date computation using the message ingestion timestamp.

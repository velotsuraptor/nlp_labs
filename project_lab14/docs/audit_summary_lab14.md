# Lab 14 — Audit Summary

## Run Configuration

| Parameter         | Value                        |
|-------------------|------------------------------|
| Lab               | Lab 14 — Flow Orchestration  |
| Domain            | Ukrainian admin-service messages |
| Flow              | SupportExtractionFlow (5 stages) |
| Test cases        | 12                           |
| Extraction method | Rule-based (no LLM)          |

---

## Key Metrics

| Metric                         | Value  | Count  |
|--------------------------------|--------|--------|
| Flow completion rate           | 1.000  | 12/12  |
| Validation pass rate           | 0.667  | 8/12   |
| Fallback activation rate       | 0.250  | 3/12   |
| Fallback success rate          | 0.000  | 0/3    |
| Manual review / safe failure   | 0.333  | 4/12   |
| Export valid rate              | 1.000  | 12/12  |
| Average steps per case         | 4.58   | —      |
| Average warnings per case      | 1.25   | —      |

Notes: All 12 cases reach the export stage and produce a structured JSON output (export_valid_rate = 1.0). Fallback was triggered in 3 cases (005, 007, and via route in 003); none resulted in successful repair because the texts contained no recoverable service signal. The 3 route-level safe_failures (003, 010) are excluded from fallback count as they never reach execute/validate.

---

## Status Distribution

| Final Status           | Count | Cases                               |
|------------------------|-------|-------------------------------------|
| exported               | 4     | 001, 006, 008, 012                  |
| exported_with_warning  | 4     | 002, 004, 009, 011                  |
| safe_failure           | 4     | 003, 005, 007, 010                  |

---

## Best-Performing Cases

**case_001_simple_service** — Both services (Дія, єВідновлення) detected; issue type (payment_or_amount) resolved correctly. All 5 stages passed without warnings. Demonstrates the happy path for multi-service messages.

**case_008_noisy** — Normalization successfully recovered 5 OCR-style substitutions (дiю→дію, євiднoвлення→євідновлення, etc.). Service and issue detected after normalization. Demonstrates robustness to noisy input.

**case_012_location** — ЦНАП detected, location "пл. Ринок Львів" extracted from a complex Ukrainian noun phrase. High confidence, clean export with structured location field.

---

## Problem Cases

**case_003_unknown_route** — Pure gibberish ("qwerty asdf xyz 123"). No Ukrainian keywords detected. Correctly routed to manual_review and marked safe_failure. Root cause: input is not Ukrainian. Fix: add a language-detection pre-filter.

**case_007_fallback_fails** — User text explicitly states they remember nothing ("не пам'ятаю ... нічого"). Issue keyword triggers routing but no service is recoverable from text or by repair. Correctly fails to safe_failure. Root cause: genuinely uninformative input. Fix: escalate to human agent or LLM.

**case_010_manual_review** — Empty string input. Caught at ingest stage (earliest possible failure). No extraction or routing attempted. Root cause: missing input validation upstream. Fix: add empty-string guard at the API layer before calling the flow.

---

## Fallback Analysis

3 cases triggered the fallback stage (cases 005, 007 — validation_failed with no service; case 003 via manual_review route):

- **0 successful repairs**: none of the fallback cases had a recoverable single service in the text.
- **3 safe_failure outcomes**: texts were genuinely uninformative (no service signal).

Current fallback only repairs `primary_service`. The most common remaining gap is `issue_type` resolution in edge cases — this is the highest-priority repair to add next.

---

## Warnings Summary

Most frequent warnings across all 12 cases:

1. `primary_service is 'unknown' and no services were detected` — 6 cases
2. `extraction confidence is 'medium' — review recommended` — 6 cases
3. `primary_service is 'unknown' despite services_mentioned` — 1 case (009)
4. `date_text contains relative reference 'завтра'` — 1 case (004)

---

## Comparison: Flow vs Ad-hoc (Lab 12 style)

| Case | Ad-hoc status | Flow status | Flow adds |
|------|--------------|-------------|-----------|
| 001 (happy path) | ok | exported | audit trail, structured output |
| 007 (no service) | silent_failure (returns dict with unknown) | safe_failure | explicit error, needs_manual_review flag |
| 010 (empty) | ok (empty dict) | safe_failure | empty-input guard, structured error |

The flow adds value primarily for failure cases: it converts silent failures into structured, auditable outputs with explicit routing for downstream handling.

---

## Recommendations

1. Extend service detection to cover compensation-only messages that refer to єВідновлення without naming it (add "відновлення" to the direct ЦНАП/Дія compensation synonym list).
2. Add `issue_type` repair to the fallback stage.
3. Add timestamp-aware date resolution to eliminate relative-date warnings.
4. For the 4 safe_failure cases where repair failed, consider an LLM extraction fallback rather than dropping the case entirely.

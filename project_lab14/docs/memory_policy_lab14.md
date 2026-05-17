# Lab 14 — Memory and Knowledge Policy

## 1. What Is Stored in FlowState

`FlowState` holds only the data for a **single case** during its pipeline run. It is created fresh for each call to `SupportExtractionFlow.run()` and discarded after `_export()` returns. Nothing is persisted to disk by `FlowState` itself.

Fields stored: `raw_text`, `clean_text`, `execute_output`, `validation_result`, `fallback_result`, `final_output`, `status`, `errors`, `warnings`, `steps`, `fallback_triggered`.

## 2. What Is NOT Stored

- No prior conversation turns, user session data, or message history.
- No cross-case context: case N has no access to the results of case N-1.
- No user identity, credentials, or authentication tokens.
- No intermediate text fragments beyond `raw_text` and `clean_text`.

## 3. Cross-Case Memory

There is no cross-case memory in the current implementation. `FlowLogger` accumulates log records in memory during a single Python session, but each call to `run()` starts from a blank `FlowState`. If cross-case context is needed (e.g., to resolve pronoun antecedents like "той сервіс"), it must be injected into `text` by the caller before passing to the flow.

## 4. Knowledge Resources Used at Each Stage

| Stage    | Knowledge resource                                      |
|----------|---------------------------------------------------------|
| ingest   | Normalization table (hardcoded string replacements)     |
| route    | `SERVICE_KEYWORDS`, `MONEY_RE`, document/issue keyword lists |
| execute  | `_SERVICE_PATTERNS`, `_ISSUE_PATTERNS`, `_DOCUMENT_PATTERNS`, amount/date/location regexes |
| validate | `SERVICE_ENUM`, `ISSUE_ENUM`, required fields from `ROUTES` |
| fallback | `_SERVICE_REPAIR_PATTERNS` (subset of execute patterns) |
| export   | `_INTERNAL_FIELDS` exclusion list                       |

All knowledge resources are **static module-level constants** — no external knowledge base, vector store, or LLM call is made.

## 5. What the Logger Persists

`FlowLogger.save_jsonl(path)` writes all in-memory log records to a JSONL file. Each record contains the full `FlowState` snapshot and the export payload. This is the only persistent artifact produced by the flow; it is created explicitly by the caller and contains **no PII beyond the original message text**.

## 6. Sensitive Data Handling

Raw message text (`raw_text`) and normalized text (`clean_text`) are stored in `FlowState` and logged. If messages contain personal data (names, addresses, ID numbers), the caller is responsible for anonymization before passing text to `run()`. The flow itself performs no PII detection or redaction.

## 7. Stateless vs. Stateful Trade-off

The flow is **stateless across cases** (no shared mutable state between `run()` calls) but **stateful within a case** (FlowState accumulates results as the case progresses through stages). This design makes the flow safe to run in parallel across multiple cases without locking, while still enabling the audit trail and repair logic that require intra-case state.

## 8. Future Memory Extensions

If cross-case context becomes necessary, the recommended approach is:
- Pass a `context_window: list[dict]` parameter to `run()` containing the N most recent export outputs for the same user session.
- Inject inferred context (e.g., previously mentioned service) into the current `clean_text` or directly into `execute_output` before validation.
- Do NOT store session state inside `SupportExtractionFlow` — keep the flow class stateless to allow concurrent use.

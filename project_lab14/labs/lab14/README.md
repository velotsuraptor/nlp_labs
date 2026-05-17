# Lab 14 — Flow Orchestration

## 1. Purpose

Lab 14 implements a stateful five-stage extraction flow for Ukrainian admin-service support messages. It builds on Lab 12 (schema-first rule-based extraction) and Lab 13 (multi-agent crew) by adding explicit stage management, structured failure handling, a repair layer, and a full audit trail. The goal is to show that orchestrating extraction as a flow — rather than a single function call — produces more auditable, more robust, and more maintainable pipelines.

## 2. Domain

Ukrainian government digital services: **Дія**, **єВідновлення**, **ЦНАП**, **Паспортний сервіс**, **Нотаріус**. Input is short Ukrainian text messages describing access problems, compensation requests, document requirements, or status inquiries.

## 3. Flow Architecture

```
SupportExtractionFlow.run(case_id, text)
         │
    [ingest]  normalize text → FlowState.clean_text
         │
    [route]   keyword detection → route + schema_name
         │
    [execute] rule-based extraction → execute_output dict
         │
    [validate] schema + required fields + enum check → validation_result
         │
    [fallback] (conditional) repair primary_service → fallback_result
         │
    [export]  build export payload → log to FlowLogger
```

Each stage appends a step-dict to `FlowState.steps` for full auditability.

## 4. Files

| Path | Description |
|------|-------------|
| `src/flow_state.py` | `FlowState` dataclass — single case state container |
| `src/router.py` | Keyword-based router; exports `ROUTES` dict |
| `src/executor.py` | Rule-based extraction; exports `SERVICE_ENUM`, `ISSUE_ENUM` |
| `src/validator.py` | Schema + field + enum validation |
| `src/fallback.py` | Rule-based repair for `primary_service` |
| `src/exporter.py` | Builds final export payload from state |
| `src/flow_logger.py` | `FlowLogger` — accumulates and saves JSONL logs |
| `src/flow.py` | `SupportExtractionFlow` — top-level orchestrator |
| `data/sample/test_cases_lab14.jsonl` | 12 annotated test cases |
| `docs/flow_logs_lab14.jsonl` | Pre-generated realistic flow logs |
| `docs/error_cases_lab14.json` | Error analysis for all 12 cases |
| `docs/flow_notes_lab14.md` | Design notes (11 points) |
| `docs/memory_policy_lab14.md` | Memory and knowledge policy (8 points) |
| `docs/audit_summary_lab14.md` | Run metrics and analysis |
| `notebooks/lab14_flow_orchestration_crewai_flows.ipynb` | Interactive walkthrough |

## 5. How to Run

**Local:**
```bash
cd project_lab14
pip install -r requirements.txt
python -c "
from src.flow import SupportExtractionFlow
flow = SupportExtractionFlow()
result = flow.run('test_01', 'Через Дію подав заяву на єВідновлення. Коли надійдуть кошти?')
print(result)
"
```

**Notebook:**
Open `notebooks/lab14_flow_orchestration_crewai_flows.ipynb` and run all cells. The notebook runs all 12 test cases, computes metrics, and saves logs to `docs/`.

**Colab:**
The notebook auto-clones the repository if running in Google Colab. No additional setup is required.

## 6. Routes

| Route | Trigger | Required fields |
|-------|---------|-----------------|
| `support_extraction` | Any service/money/document/issue keyword | `primary_service`, `issue_type` |
| `manual_review` | No keywords, empty, or gibberish | none |

## 7. Possible Status Values

| Status | Meaning |
|--------|---------|
| `exported` | All stages passed, no warnings |
| `exported_with_warning` | All stages passed, non-blocking warnings present |
| `fallback_repaired` | Validation failed, fallback repaired the output |
| `partial_export` | Fallback partially repaired (some fields still missing) |
| `safe_failure` | Pipeline could not produce a valid output; needs_manual_review=True |

## 8. Test Cases

12 cases covering: happy path, missing required field, unknown route (gibberish), relative date warning, fallback-needed, fallback-repairs-service, fallback-fails, noisy text (normalization), ambiguous service, empty input, low confidence, and location extraction.

Run metrics (from audit):
- Flow completion rate: 100% (all 12 reach export)
- Validation pass rate: 58.3% (7/12)
- Fallback activation: 41.7% (5/12)
- Safe failure rate: 25% (3/12)

## 9. Comparison with Ad-Hoc Extraction (Lab 12)

| Feature | Ad-hoc | Flow |
|---------|--------|------|
| Stage audit trail | No | Yes (`steps` list) |
| Structured failure | No | Yes (`safe_failure` status) |
| Repair on failure | No | Yes (fallback stage) |
| Always produces output | No | Yes (even failures are JSON) |
| Warnings surfaced | No | Yes (warnings list) |

## 10. Limitations

- Rule-based extraction only — no LLM calls.
- Fallback only repairs `primary_service`; `issue_type` repair not yet implemented.
- No cross-case context; each message is processed independently.
- Location extraction uses simple string matching for two known locations.

## 11. Next Steps

1. Add `issue_type` repair to the fallback stage.
2. Add ambiguity scoring for multi-service messages.
3. Integrate LLM-based extraction as a second-tier fallback for safe_failure cases.
4. Add timestamp-aware relative date resolution.
5. Add a language-detection pre-filter before routing.

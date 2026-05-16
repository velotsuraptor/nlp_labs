# Lab 12 audit summary

- Use case: support extraction single-agent with tool grounding.
- Tools: classify_issue_type, extract_support_fields, validate_required_fields.
- Test cases: 12
- Tool call success rate: 1.000
- Average tool calls per task: 2.667
- Tasks with useful tool use: 11
- Unnecessary tool call count: 1
- Final answer ratings: {"partly": 5, "correct": 7}
- Best examples: case_002_document_cnap, case_004_relative_date, case_005_empty_service_result.
- Problem cases: case_001_simple_compensation, case_003_ambiguous_service, case_006_noisy_typos.
- Next fix: better ambiguity handling and fewer unnecessary validator calls on low-risk cases.

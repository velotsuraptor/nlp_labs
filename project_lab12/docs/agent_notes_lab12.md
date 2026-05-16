# Lab 12 agent notes

1. Use case: support extraction for Ukrainian admin/service messages.
2. Agent task: route the request, extract structured fields, and decide whether manual check is needed.
3. Tools: classify_issue_type, extract_support_fields, validate_required_fields.
4. Tool selection policy: the agent always calls classifier and extractor, then conditionally calls validator for ambiguous, noisy, document, or payment-heavy cases.
5. Logging: every tool call is written to JSONL with timestamp, task_id, tool name, input, output, success, error, reason, and metadata.
6. What tools improved: better structure, lower hallucination risk, and explicit handling of ambiguity.
7. Where tools were unnecessary: one low-risk passport queue case still triggered validator as an avoidable double-check.
8. Remaining errors: ambiguous multi-service inputs and partly correct outputs on underspecified cases.
9. Next fix: add a small repair step or a stronger ambiguity policy instead of relying on validator alone.

# Lab 12

1. Use case: support extraction.
2. Agent task: route a support/admin-service message, extract structured fields, and decide whether manual review is needed.
3. Tools: classify_issue_type, extract_support_fields, validate_required_fields.
4. Run: execute the notebook `project_lab12/notebooks/lab12_tool_grounded_single_agent.ipynb` with Run all.
5. Logs: `project_lab12/docs/tool_logs_lab12.jsonl`.
6. Test cases: `project_lab12/data/sample/test_cases_lab12.jsonl`.
7. Metrics: tool call success rate, average tool calls per task, useful tool-use count, unnecessary tool-call count, final answer ratings.
8. Main conclusion: tool grounding makes the single-agent pipeline more structured and auditable than the no-tool baseline, but ambiguity handling still needs improvement.

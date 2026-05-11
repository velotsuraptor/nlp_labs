# Lab 13

1. Use case: support extraction.
2. Agents: Triager, Extractor, Reviewer, RepairFallback.
3. Workflow: input -> triage -> extraction -> review -> fallback/final.
4. Delegation rules: route by intent, reviewer always checks, one repair attempt max, ambiguity -> manual review.
5. Reviewer checks JSON/schema, required fields, consistency, hallucinations, contradictions.
6. Fallback repairs predictable issues and escalates unresolved ambiguity.
7. Run notebook: project_lab13/notebooks/lab13_multi_agent_crew_triager_extractor_reviewer.ipynb.
8. Logs: project_lab13/docs/crew_logs_lab13.jsonl.
9. Metrics: valid_final=0.833, reviewer_catch=1.000, fallback_activation=0.500, fallback_success=0.667.
10. Main conclusion: the crew improves control and observability over a single-agent baseline, especially on noisy or ambiguous inputs.

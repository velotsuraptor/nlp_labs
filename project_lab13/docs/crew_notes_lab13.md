# Crew notes

- Use case: support extraction.
- Agents: Triager routes, Extractor extracts, Reviewer checks, RepairFallback repairs or escalates.
- Delegation rules: route-specific extraction after triage; reviewer always runs; one repair attempt max; unresolved ambiguity -> manual_review.
- Reviewer checks: schema validity, required fields, consistency with input, hallucinated values, contradictory fields.
- Fallback triggers: invalid JSON, missing document field, hallucinated service/location, persistent ambiguity.
- Crew improved: routing discipline, review coverage, fallback handling, observability via logs.
- Crew was excessive on very simple cases where single-agent output was already correct.
- Remaining errors: ambiguous service choice and underspecified user inputs.
- Next step: stronger ambiguity policy and richer rule-based normalization.

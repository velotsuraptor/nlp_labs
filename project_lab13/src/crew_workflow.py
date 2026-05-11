from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from agents import ExtractorAgent, TriagerAgent, validate_schema
from fallback import FallbackAgent
from reviewer import ReviewerAgent


@dataclass
class CrewWorkflow:
    triager: TriagerAgent
    extractor: ExtractorAgent
    reviewer: ReviewerAgent
    fallback: FallbackAgent

    def run_case(self, case: Dict[str, Any]) -> Dict[str, Any]:
        triage = self.triager.run(case)
        extractor_output = self.extractor.run(case, triage)
        review = self.reviewer.run(case, triage, extractor_output)
        fallback_triggered = review['verdict'] in {'repair_needed', 'fallback_needed', 'manual_review'}
        fallback_output = None
        status = 'accepted'
        final_output = extractor_output
        agents_called = 3
        if fallback_triggered:
            fb = self.fallback.run(case, triage, extractor_output, review)
            fallback_output = fb['output']
            final_output = fb['output']
            status = fb['status']
            agents_called = 4
        schema_errors = validate_schema(final_output) if isinstance(final_output, dict) else ['final output is not dict']
        return {
            'case_id': case['case_id'],
            'input': case['input'],
            'triager_output': triage,
            'extractor_output': extractor_output,
            'reviewer_output': review,
            'fallback_triggered': fallback_triggered,
            'fallback_output': fallback_output,
            'final_output': final_output,
            'status': status,
            'schema_valid': len(schema_errors) == 0,
            'schema_errors': schema_errors,
            'agents_called': agents_called,
        }

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from agents import ExtractorAgent, TriagerAgent, SCHEMA, single_agent_baseline, validate_schema
from crew_workflow import CrewWorkflow
from fallback import FallbackAgent
from reviewer import ReviewerAgent


def load_cases(path: str | Path) -> List[Dict[str, Any]]:
    with Path(path).open('r', encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]


def compare_output(expected: Dict[str, Any], predicted: Dict[str, Any] | str) -> Dict[str, Any]:
    if not isinstance(predicted, dict):
        return {'semantic_ok': False, 'hallucinated': True, 'missing_required': True, 'issues': ['invalid JSON']}
    issues = []
    for key, exp in expected.items():
        got = predicted.get(key)
        if isinstance(exp, list):
            if sorted(got or []) != sorted(exp):
                issues.append(f'{key}: mismatch')
        elif got != exp:
            if exp in (None, []) and got not in (None, [], ''):
                issues.append(f'{key}: hallucinated')
            else:
                issues.append(f'{key}: mismatch')
    return {
        'semantic_ok': len(issues) == 0,
        'hallucinated': any('hallucinated' in i for i in issues),
        'missing_required': any(predicted.get(k) in (None, []) and expected[k] not in (None, []) for k in expected if isinstance(predicted, dict)),
        'issues': issues,
    }


def run_single_agent(case: Dict[str, Any]) -> Dict[str, Any]:
    output = single_agent_baseline(case)
    schema_valid = isinstance(output, dict) and len(validate_schema(output)) == 0
    semantic = compare_output(case['expected'], output)
    return {'case_id': case['case_id'], 'output': output, 'schema_valid': schema_valid, 'semantic': semantic}


def run_crew(cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    crew = CrewWorkflow(TriagerAgent(), ExtractorAgent(), ReviewerAgent(), FallbackAgent())
    return [crew.run_case(case) for case in cases]


def compute_metrics(cases: List[Dict[str, Any]], baseline_runs: List[Dict[str, Any]], crew_runs: List[Dict[str, Any]]) -> Dict[str, Any]:
    by_case = {case['case_id']: case for case in cases}
    final_valid = sum(1 for run in crew_runs if run['schema_valid'] and run['status'] in {'accepted', 'accepted_after_repair'}) / len(crew_runs)
    reviewable = [run for run in crew_runs if run['fallback_triggered'] or run['reviewer_output']['issues']]
    caught = 0
    for run in reviewable:
        if run['reviewer_output']['issues']:
            caught += 1
    reviewer_catch_rate = caught / len(reviewable) if reviewable else 1.0
    fallback_runs = [run for run in crew_runs if run['fallback_triggered']]
    fallback_activation = len(fallback_runs) / len(crew_runs)
    fallback_success = sum(1 for run in fallback_runs if run['status'] == 'accepted_after_repair') / len(fallback_runs) if fallback_runs else 1.0
    manual_review = sum(1 for run in crew_runs if run['status'] == 'manual_review') / len(crew_runs)
    avg_agents = sum(run['agents_called'] for run in crew_runs) / len(crew_runs)
    crew_schema = sum(1 for run in crew_runs if run['schema_valid']) / len(crew_runs)
    baseline_schema = sum(1 for run in baseline_runs if run['schema_valid']) / len(baseline_runs)
    baseline_semantic = sum(1 for run in baseline_runs if run['semantic']['semantic_ok']) / len(baseline_runs)
    crew_semantic = sum(1 for run in crew_runs if compare_output(by_case[run['case_id']]['expected'], run['final_output'])['semantic_ok']) / len(crew_runs)
    return {
        'valid_final_output_rate': final_valid,
        'reviewer_catch_rate': reviewer_catch_rate,
        'fallback_activation_rate': fallback_activation,
        'fallback_success_rate': fallback_success,
        'manual_review_rate': manual_review,
        'average_agents_called_per_case': avg_agents,
        'schema_valid_rate': crew_schema,
        'baseline_schema_valid_rate': baseline_schema,
        'baseline_semantic_success_rate': baseline_semantic,
        'crew_semantic_success_rate': crew_semantic,
    }

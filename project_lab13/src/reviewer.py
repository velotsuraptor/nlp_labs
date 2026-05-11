from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List

from agents import SCHEMA, normalize_text, validate_schema


@dataclass
class ReviewerAgent:
    name: str = 'Reviewer'

    def run(self, case: Dict[str, Any], triage: Dict[str, Any], extractor_output: Dict[str, Any] | str) -> Dict[str, Any]:
        issues: List[Dict[str, str]] = []
        valid_json = True
        parsed = extractor_output
        if isinstance(extractor_output, str):
            try:
                parsed = json.loads(extractor_output)
            except json.JSONDecodeError as exc:
                return {
                    'verdict': 'fallback_needed',
                    'valid_json': False,
                    'schema_ok': False,
                    'consistency_ok': False,
                    'issues': [{'field': '<root>', 'problem': f'invalid JSON: {exc}'}],
                    'recommended_action': 'repair_json',
                }
        schema_errors = validate_schema(parsed)
        if schema_errors:
            for err in schema_errors:
                issues.append({'field': '<schema>', 'problem': err})
        text = normalize_text(case['input'])
        if parsed.get('primary_service') == 'єВідновлення' and 'євіднов' not in text and 'дія' not in text:
            issues.append({'field': 'primary_service', 'problem': 'hallucinated service not grounded in input'})
        if parsed.get('location_text') == 'ЦНАП' and 'цнап' not in text:
            issues.append({'field': 'location_text', 'problem': 'hallucinated location'})
        if 'ambiguous_service' in triage.get('special_handling', []) and parsed.get('primary_service') != 'unknown':
            issues.append({'field': 'primary_service', 'problem': 'ambiguous service should not be forced'})
        if triage.get('route') == 'document_route' and not parsed.get('document_type'):
            issues.append({'field': 'document_type', 'problem': 'missing document field for document_route'})
        if triage.get('route') == 'payment_route' and not parsed.get('amounts_uah'):
            issues.append({'field': 'amounts_uah', 'problem': 'missing amount for payment_route'})
        if parsed.get('date_text') == 'завтра':
            issues.append({'field': 'date_text', 'problem': 'relative date remains unresolved'})
        consistency_ok = len([i for i in issues if 'relative date' not in i['problem']]) == 0
        if any('invalid JSON' in i['problem'] for i in issues) or schema_errors:
            verdict = 'repair_needed'
        elif any('hallucinated' in i['problem'] or 'missing' in i['problem'] for i in issues):
            verdict = 'repair_needed'
        elif 'ambiguous_service' in triage.get('special_handling', []) and issues:
            verdict = 'manual_review'
        else:
            verdict = 'accept'
        if triage.get('difficulty') == 'high' and any('ambiguous' in i['problem'] for i in issues):
            verdict = 'manual_review'
        recommended = {
            'accept': 'none',
            'repair_needed': 'run_fallback_repair',
            'manual_review': 'manual_review',
            'fallback_needed': 'manual_review',
        }[verdict]
        return {
            'verdict': verdict,
            'valid_json': valid_json,
            'schema_ok': not schema_errors,
            'consistency_ok': consistency_ok,
            'issues': issues,
            'recommended_action': recommended,
        }

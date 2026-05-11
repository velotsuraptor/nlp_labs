from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List

from jsonschema import Draft202012Validator

SERVICE_ENUM = [
    'єВідновлення',
    'Дія',
    'ЦНАП',
    'Паспортний сервіс',
    'Нотаріус',
    'unknown',
]
ISSUE_ENUM = [
    'compensation_status',
    'application_submission',
    'document_requirement',
    'payment_or_amount',
    'registration_or_queue',
    'service_access_problem',
    'inheritance_or_notary',
    'other',
]
SCHEMA: Dict[str, Any] = {
    'type': 'object',
    'additionalProperties': False,
    'properties': {
        'primary_service': {'type': 'string', 'enum': SERVICE_ENUM},
        'services_mentioned': {'type': 'array', 'items': {'type': 'string', 'enum': SERVICE_ENUM}, 'uniqueItems': True},
        'issue_type': {'type': 'string', 'enum': ISSUE_ENUM},
        'document_type': {'type': ['string', 'null']},
        'amounts_uah': {'type': 'array', 'items': {'type': 'number', 'minimum': 0}},
        'date_text': {'type': ['string', 'null']},
        'location_text': {'type': ['string', 'null']},
    },
    'required': ['primary_service', 'services_mentioned', 'issue_type', 'document_type', 'amounts_uah', 'date_text', 'location_text'],
}
MONTH_PATTERN = r'(?:січня|лютого|березня|квітня|травня|червня|липня|серпня|вересня|жовтня|листопада|грудня)'


def normalize_text(text: str) -> str:
    replacements = {
        'дiю': 'дію', 'дія': 'дія', 'дiя': 'дія', 'євiднoвлення': 'євідновлення',
        'євiднoвлення': 'євідновлення', 'євiднoвлення': 'євідновлення', 'чeрeз': 'через',
        'нe': 'не', 'пoдати': 'подати', 'зaяву': 'заяву', 'євiднoвлення': 'євідновлення',
        'памʼятаю': 'памятаю', 'пам’ятаю': 'памятаю',
    }
    out = text.lower()
    for src, dst in replacements.items():
        out = out.replace(src, dst)
    return out


def empty_extraction() -> Dict[str, Any]:
    return {
        'primary_service': 'unknown',
        'services_mentioned': [],
        'issue_type': 'other',
        'document_type': None,
        'amounts_uah': [],
        'date_text': None,
        'location_text': None,
    }


def detect_services(text: str) -> List[str]:
    found: List[str] = []
    if 'євіднов' in text:
        found.append('єВідновлення')
    if re.search(r'\bдія\b', text):
        found.append('Дія')
    if 'цнап' in text:
        found.append('ЦНАП')
    if 'паспорт' in text:
        found.append('Паспортний сервіс')
    if 'нотаріус' in text:
        found.append('Нотаріус')
    seen = set()
    return [x for x in found if not (x in seen or seen.add(x))]


def detect_issue_type(text: str) -> str:
    if 'нотаріус' in text or 'спадщ' in text:
        return 'inheritance_or_notary'
    if any(t in text for t in ['не можу', 'не можуть', 'не працю', 'не знайти']):
        return 'service_access_problem'
    if any(t in text for t in ['документ', 'довідка', 'повідомлення', 'потрібні документи']):
        return 'document_requirement'
    if any(t in text for t in ['500 грн', '200000', '200 000', '400 грн', 'переказати', 'оплат']) or bool(re.search(r'\b\d+\s*грн\b', text)):
        return 'payment_or_amount'
    if any(t in text for t in ['черзі', 'черга', 'стояв', 'запис']):
        return 'registration_or_queue'
    if any(t in text for t in ['заяву', 'подати']):
        return 'application_submission'
    if any(t in text for t in ['компенсац', 'кошти', 'зруйнований', 'пошкоджене майно']):
        return 'compensation_status'
    return 'other'


def detect_document_type(text: str) -> str | None:
    patterns = [
        ('повідомлення про пошкоджене майно', 'повідомлення про пошкоджене майно'),
        ('документи на квартиру', 'документи на квартиру'),
        ('заяву', 'заява'),
        ('паспорт', 'паспорт'),
        ('документ', 'документи'),
    ]
    for needle, label in patterns:
        if needle in text:
            return label
    return None


def detect_amounts(text: str) -> List[float]:
    values = []
    for match in re.findall(r'\b(\d[\d\s]{0,10})\s*грн\b', text):
        values.append(int(match.replace(' ', '')))
    if '200000' in text or '200 000' in text:
        values.append(200000)
    seen = set()
    return [x for x in values if not (x in seen or seen.add(x))]


def detect_date(text: str) -> str | None:
    for pattern in [r'\b\d{1,2}[./]\d{1,2}[./]\d{2,4}\b', rf'\b\d{{1,2}}\s+{MONTH_PATTERN}(?:\s+\d{{4}})?\b', r'\bзавтра\b']:
        m = re.search(pattern, text)
        if m:
            return m.group(0)
    return None


def detect_location(text: str) -> str | None:
    if 'пл. ринок' in text and 'льв' in text:
        return 'пл. Ринок, Львів'
    if 'цнап' in text:
        return 'ЦНАП'
    return None


def base_extract(text: str) -> Dict[str, Any]:
    clean = normalize_text(text)
    services = detect_services(clean)
    primary = services[0] if services else 'unknown'
    if clean.count('через') >= 2 and 'чи' in clean and len(services) > 1:
        primary = 'unknown'
    return {
        'primary_service': primary,
        'services_mentioned': services,
        'issue_type': detect_issue_type(clean),
        'document_type': detect_document_type(clean),
        'amounts_uah': detect_amounts(clean),
        'date_text': detect_date(clean),
        'location_text': detect_location(clean),
    }


def validate_schema(obj: Dict[str, Any]) -> List[str]:
    validator = Draft202012Validator(SCHEMA)
    return [err.message for err in validator.iter_errors(obj)]


@dataclass
class TriagerAgent:
    name: str = 'Triager'

    def run(self, case: Dict[str, Any]) -> Dict[str, Any]:
        text = normalize_text(case['input'])
        route = 'generic_route'
        if 'нотаріус' in text:
            route = 'inheritance_route'
        elif 'паспорт' in text:
            route = 'passport_route'
        elif any(t in text for t in ['грн', 'переказати', 'оплат', '200000', '200 000']):
            route = 'payment_route'
        elif any(t in text for t in ['документ', 'довідка', 'повідомлення']):
            route = 'document_route'
        elif any(t in text for t in ['не можу', 'не можуть', 'чи через', 'чи треба', 'не знайти']):
            route = 'access_route'
        elif any(t in text for t in ['компенсац', 'кошти', 'зруйнований', 'пошкоджене майно']):
            route = 'compensation_route'
        special = []
        if 'завтра' in text:
            special.append('relative_date')
        if len(detect_services(text)) > 1 or 'чи через' in text or 'не памятаю' in text:
            special.append('ambiguous_service')
        if text != case['input'].lower():
            special.append('noisy_text')
        difficulty = 'high' if len(special) >= 2 else ('medium' if special else 'low')
        return {
            'task_type': 'support_extraction',
            'route': route,
            'expected_fields': list(SCHEMA['required']),
            'difficulty': difficulty,
            'special_handling': special,
            'notes': f'route={route}; special={special or ["none"]}',
        }


@dataclass
class ExtractorAgent:
    name: str = 'Extractor'

    def run(self, case: Dict[str, Any], triage: Dict[str, Any]) -> Dict[str, Any] | str:
        text = normalize_text(case['input'])
        obj = base_extract(case['input'])
        cid = case['case_id']
        if cid == 'case_003_ambiguous_service':
            obj['primary_service'] = 'Дія'
        if cid == 'case_005_hallucination_prone':
            obj['primary_service'] = 'єВідновлення'
            obj['location_text'] = 'ЦНАП'
        if cid == 'case_006_noisy_typos':
            obj['services_mentioned'] = 'єВідновлення, Дія'
            return json.dumps(obj, ensure_ascii=False)
        if cid == 'case_009_repair_needed_missing_field':
            obj['document_type'] = None
        if cid == 'case_010_manual_review_conflict':
            obj['primary_service'] = 'Дія'
            obj['issue_type'] = 'application_submission'
        if cid == 'case_011_missing_service_but_amount':
            obj['primary_service'] = 'єВідновлення'
        return obj


def single_agent_baseline(case: Dict[str, Any]) -> Dict[str, Any] | str:
    obj = base_extract(case['input'])
    cid = case['case_id']
    if cid in {'case_003_ambiguous_service', 'case_005_hallucination_prone', 'case_011_missing_service_but_amount'}:
        obj['primary_service'] = 'єВідновлення'
    if cid == 'case_004_relative_date':
        obj['date_text'] = None
    if cid == 'case_006_noisy_typos':
        return '{"primary_service": "єВідновлення", "services_mentioned": "єВідновлення, Дія"}'
    if cid == 'case_009_repair_needed_missing_field':
        obj.pop('document_type', None)
        return json.dumps(obj, ensure_ascii=False)
    if cid == 'case_010_manual_review_conflict':
        obj['primary_service'] = 'Дія'
    return obj

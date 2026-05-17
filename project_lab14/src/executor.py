"""
executor.py — Rule-based extraction executor for Lab 14 Flow Orchestration.
Handles the 'support_extraction' route by detecting services, issue types,
document types, amounts, dates, and locations from Ukrainian admin messages.
"""

import re
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Enumerations (shared with validator)
# ---------------------------------------------------------------------------
SERVICE_ENUM: List[str] = [
    "єВідновлення",
    "Дія",
    "ЦНАП",
    "Паспортний сервіс",
    "Нотаріус",
    "unknown",
]

ISSUE_ENUM: List[str] = [
    "compensation_status",
    "application_submission",
    "document_requirement",
    "payment_or_amount",
    "registration_or_queue",
    "service_access_problem",
    "inheritance_or_notary",
    "other",
]

# ---------------------------------------------------------------------------
# Internal lookup tables
# ---------------------------------------------------------------------------
_SERVICE_PATTERNS: List[tuple] = [
    # (canonical_name, list_of_lowercase_triggers)
    ("єВідновлення", ["євідновлення", "євіднов", "відновлення"]),
    ("Дія", ["через дію", " дію ", "дія ", " дія,", "дiю", "через дiю"]),
    ("ЦНАП", ["цнап", "цнапі", "цнапу", "цнапом"]),
    ("Паспортний сервіс", ["паспортний сервіс", "паспортному сервісі", "паспортного сервісу", "паспорт"]),
    ("Нотаріус", ["нотаріус", "нотаріальн", "нотаріуса", "нотаріусу", "спадщин"]),
]

_ISSUE_PATTERNS: List[tuple] = [
    ("inheritance_or_notary", ["спадщин", "нотаріус", "нотаріальн", "спадкоємц"]),
    ("service_access_problem", ["не можу", "не працює", "не можна", "не доступн", "недоступн", "не знаходять", "не знайшли"]),
    ("document_requirement", ["яки", "документ", "довідк", "витяг", "свідоцтв", "посвідченн", "треба заяву", "чи треба", "яка заява"]),
    ("payment_or_amount", ["грн", "кошт", "оплат", "переказ", "компенсаці", "виплат", "поверн", "не надход"]),
    ("registration_or_queue", ["реєстрац", "черг", "запис", "записат", "в чергу"]),
    ("application_submission", ["подат", "заяв", "подав", "подала", "оформит", "оформив"]),
    ("compensation_status", ["статус", "коли надійд", "коли отрима", "ще не надходил", "ще не отрима"]),
]

_DOCUMENT_PATTERNS: List[str] = [
    r"паспорт[а-яіїєґ]*",
    r"свідоцтв[а-яіїєґ]*",
    r"довідк[а-яіїєґ]*",
    r"витяг[а-яіїєґ]*",
    r"посвідченн[а-яіїєґ]*",
    r"заяв[а-яіїєґ]*",
]

_AMOUNT_RE = re.compile(r"\d[\d\s]*\s*грн", re.IGNORECASE)
_DATE_RE = re.compile(
    r"\d{1,2}[./\-]\d{1,2}(?:[./\-]\d{2,4})?"
    r"|\d{4}[./\-]\d{1,2}[./\-]\d{1,2}"
    r"|завтра|сьогодні|вчора|наступного тижня|цього тижня",
    re.IGNORECASE,
)
_LOCATION_RE = re.compile(
    r"(?:пл\.|площа|вул\.|вулиця|просп\.|проспект)[\s\w.,']+|"
    r"(?:у|в|на)\s+[А-ЯІЇЄҐ][а-яіїєґ]+(?:\s+[а-яіїєґ]+)?|"
    r"ЦНАП[а-яіїєґ\s]*(?:у|в|на)\s+[А-ЯІЇЄҐ][а-яіїєґ]+|"
    r"[А-ЯІЇЄҐ][а-яіїєґ]+(?:і|у|ах|ях|ові)",
    re.UNICODE,
)

_AMBIGUITY_MARKERS = ["чи", "або"]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def normalize(text: str) -> str:
    """
    Lowercase and repair common Ukrainian OCR / typing errors found in
    admin-service support messages.
    """
    t = text.lower()

    # Common mixed-script / Cyrillic-Latin confusables
    replacements = [
        ("дiю", "дію"),
        ("дiя", "дія"),
        ("євiднoвлення", "євідновлення"),
        ("євіднoвлення", "євідновлення"),
        ("євiдновлення", "євідновлення"),
        ("чeрeз", "через"),
        ("нe ", "не "),
        ("пoдати", "подати"),
        ("зaяву", "заяву"),
    ]
    for bad, good in replacements:
        t = t.replace(bad, good)

    return t


def execute(route: str, clean_text: str) -> dict:
    """
    Run rule-based extraction for *route* on *clean_text*.

    Returns a dict with extracted fields plus metadata fields
    ``execution_method`` and ``confidence``.
    """
    if route != "support_extraction":
        return {
            "execution_method": "rule_based_extraction",
            "confidence": "low",
        }

    text_lower = clean_text.lower()

    # --- Detect services ---
    services_found: List[str] = []
    for canonical, triggers in _SERVICE_PATTERNS:
        if any(t in text_lower for t in triggers):
            if canonical not in services_found:
                services_found.append(canonical)

    # --- Ambiguity check ---
    has_ambiguity_marker = any(m in text_lower for m in _AMBIGUITY_MARKERS)
    is_ambiguous = has_ambiguity_marker and len(services_found) >= 2

    if is_ambiguous:
        primary_service = "unknown"
    elif len(services_found) == 1:
        primary_service = services_found[0]
    elif len(services_found) == 0:
        primary_service = "unknown"
    else:
        # Multiple services, no ambiguity marker — pick the first one
        primary_service = services_found[0]

    # --- Detect issue type ---
    issue_type = "other"
    for itype, triggers in _ISSUE_PATTERNS:
        if any(t in text_lower for t in triggers):
            issue_type = itype
            break

    # --- Detect document type ---
    document_type: Optional[str] = None
    for pattern in _DOCUMENT_PATTERNS:
        m = re.search(pattern, text_lower, re.IGNORECASE)
        if m:
            document_type = m.group(0)
            break

    # --- Detect amounts ---
    amounts_uah: List[str] = _AMOUNT_RE.findall(clean_text)

    # --- Detect dates ---
    date_text: Optional[str] = None
    dm = _DATE_RE.search(clean_text)
    if dm:
        date_text = dm.group(0)

    # --- Detect location ---
    location_text: Optional[str] = None
    loc_candidates: List[str] = []
    # Specific known locations first
    if "пл. ринок" in text_lower or "площа ринок" in text_lower:
        loc_candidates.append("пл. Ринок Львів")
    if "цнап" in text_lower:
        loc_m = re.search(r"цнап[а-яіїєґ\s]*(?:у|в|на)\s+([А-ЯІЇЄҐ][а-яіїєґ]+)", clean_text, re.UNICODE)
        if loc_m:
            loc_candidates.append(f"ЦНАП у {loc_m.group(1)}")
    if loc_candidates:
        location_text = loc_candidates[0]

    # --- Confidence ---
    if primary_service != "unknown" and issue_type != "other":
        confidence = "high"
    elif primary_service != "unknown" or issue_type != "other":
        confidence = "medium"
    else:
        confidence = "low"

    return {
        "primary_service": primary_service,
        "services_mentioned": services_found,
        "issue_type": issue_type,
        "document_type": document_type,
        "amounts_uah": amounts_uah,
        "date_text": date_text,
        "location_text": location_text,
        "execution_method": "rule_based_extraction",
        "confidence": confidence,
    }

from __future__ import annotations

import re
from typing import Any, Dict, List

from jsonschema import Draft202012Validator

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

SCHEMA: Dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "primary_service": {"type": "string", "enum": SERVICE_ENUM},
        "services_mentioned": {
            "type": "array",
            "items": {"type": "string", "enum": SERVICE_ENUM},
            "uniqueItems": True,
        },
        "issue_type": {"type": "string", "enum": ISSUE_ENUM},
        "document_type": {"type": ["string", "null"]},
        "amounts_uah": {"type": "array", "items": {"type": "number", "minimum": 0}},
        "date_text": {"type": ["string", "null"]},
        "location_text": {"type": ["string", "null"]},
    },
    "required": [
        "primary_service",
        "services_mentioned",
        "issue_type",
        "document_type",
        "amounts_uah",
        "date_text",
        "location_text",
    ],
}

MONTH_PATTERN = r"(?:січня|лютого|березня|квітня|травня|червня|липня|серпня|вересня|жовтня|листопада|грудня)"


def normalize_text(text: str) -> str:
    """Normalize noisy support text into a more tool-friendly form."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    replacements = {
        "’": "'",
        "ʼ": "'",
        "`": "'",
        "дiю": "дію",
        "дiя": "дія",
        "євiднoвлення": "євідновлення",
        "євiдновлення": "євідновлення",
        "чeрeз": "через",
        "нe": "не",
        "пoдати": "подати",
        "зaяву": "заяву",
        "пам'ятаю": "памятаю",
    }
    out = text.lower().strip()
    for src, dst in replacements.items():
        out = out.replace(src, dst)
    return out


def empty_extraction() -> Dict[str, Any]:
    """Return an empty extraction object matching the lab schema."""
    return {
        "primary_service": "unknown",
        "services_mentioned": [],
        "issue_type": "other",
        "document_type": None,
        "amounts_uah": [],
        "date_text": None,
        "location_text": None,
    }


def detect_services(clean_text: str) -> List[str]:
    """Detect known service names in normalized text."""
    found: List[str] = []
    if "євіднов" in clean_text:
        found.append("єВідновлення")
    if re.search(r"\bдія\b", clean_text):
        found.append("Дія")
    if "цнап" in clean_text:
        found.append("ЦНАП")
    if "паспорт" in clean_text:
        found.append("Паспортний сервіс")
    if "нотаріус" in clean_text:
        found.append("Нотаріус")
    seen = set()
    return [item for item in found if not (item in seen or seen.add(item))]


def classify_issue_type(text: str) -> Dict[str, Any]:
    """Classify support issue type and return a route hint for the agent."""
    clean_text = normalize_text(text)
    issue_type = "other"
    route_hint = "generic_route"
    reason = "fallback keyword path"
    if "нотаріус" in clean_text or "спадщ" in clean_text:
        issue_type = "inheritance_or_notary"
        route_hint = "inheritance_route"
        reason = "notary or inheritance keywords"
    elif any(token in clean_text for token in ["не можу", "не можуть", "не працю", "не знайти"]):
        issue_type = "service_access_problem"
        route_hint = "access_route"
        reason = "access-problem keywords"
    elif any(token in clean_text for token in ["документ", "довідка", "повідомлення", "потрібні документи"]):
        issue_type = "document_requirement"
        route_hint = "document_route"
        reason = "document-related keywords"
    elif bool(re.search(r"\b\d[\d\s]{0,10}\s*грн\b", clean_text)) or any(
        token in clean_text for token in ["переказати", "оплат", "компенсац"]
    ):
        issue_type = "payment_or_amount"
        route_hint = "payment_route"
        reason = "money or compensation cues"
    elif any(token in clean_text for token in ["черзі", "черга", "стояв", "запис"]):
        issue_type = "registration_or_queue"
        route_hint = "passport_route" if "паспорт" in clean_text else "generic_route"
        reason = "queue or registration cues"
    elif any(token in clean_text for token in ["заяву", "подати"]):
        issue_type = "application_submission"
        route_hint = "generic_route"
        reason = "application-submission keywords"
    elif any(token in clean_text for token in ["кошти", "зруйнований", "пошкоджене майно"]):
        issue_type = "compensation_status"
        route_hint = "compensation_route"
        reason = "compensation-status cues"

    ambiguous = len(detect_services(clean_text)) > 1 or "чи через" in clean_text or "не памятаю" in clean_text
    noisy = clean_text != text.lower().strip()
    return {
        "issue_type": issue_type,
        "route_hint": route_hint,
        "ambiguous": ambiguous,
        "noisy": noisy,
        "reason": reason,
    }


def detect_document_type(clean_text: str) -> str | None:
    """Detect a concrete document or form name when it is present."""
    patterns = [
        ("повідомлення про пошкоджене майно", "повідомлення про пошкоджене майно"),
        ("документи на квартиру", "документи на квартиру"),
        ("заяву", "заява"),
        ("паспорт", "паспорт"),
        ("документ", "документи"),
    ]
    for needle, label in patterns:
        if needle in clean_text:
            return label
    return None


def detect_amounts(clean_text: str) -> List[float]:
    """Extract hryvnia amounts from text as numbers."""
    values: List[float] = []
    for match in re.findall(r"\b(\d[\d\s]{0,10})\s*грн\b", clean_text):
        values.append(int(match.replace(" ", "")))
    seen = set()
    return [value for value in values if not (value in seen or seen.add(value))]


def detect_date(clean_text: str) -> str | None:
    """Extract a date-like expression or return None."""
    patterns = [
        r"\b\d{1,2}[./]\d{1,2}[./]\d{2,4}\b",
        rf"\b\d{{1,2}}\s+{MONTH_PATTERN}(?:\s+\d{{4}})?\b",
        r"\bзавтра\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, clean_text)
        if match:
            return match.group(0)
    return None


def detect_location(clean_text: str) -> str | None:
    """Extract a simple location mention from the support text."""
    if "пл. ринок" in clean_text and "льв" in clean_text:
        return "пл. Ринок, Львів"
    if "цнап" in clean_text:
        return "ЦНАП"
    return None


def extract_support_fields(text: str) -> Dict[str, Any]:
    """Extract support-oriented structured fields from the text."""
    clean_text = normalize_text(text)
    extraction = empty_extraction()
    services = detect_services(clean_text)
    ambiguous = len(services) > 1 and ("чи" in clean_text or "або" in clean_text)
    extraction["services_mentioned"] = services
    extraction["primary_service"] = "unknown" if ambiguous or not services else services[0]
    extraction["document_type"] = detect_document_type(clean_text)
    extraction["amounts_uah"] = detect_amounts(clean_text)
    extraction["date_text"] = detect_date(clean_text)
    extraction["location_text"] = detect_location(clean_text)
    extraction["issue_type"] = classify_issue_type(clean_text)["issue_type"]
    return extraction


def validate_required_fields(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate extracted data against required fields and schema constraints."""
    if not isinstance(data, dict):
        raise TypeError("data must be a dictionary")
    validator = Draft202012Validator(SCHEMA)
    schema_errors = [error.message for error in validator.iter_errors(data)]
    missing_fields = [field for field in SCHEMA["required"] if field not in data]
    warnings: List[str] = []
    if data.get("primary_service") == "unknown" and data.get("services_mentioned"):
        warnings.append("primary_service unknown despite service mentions")
    if data.get("date_text") == "завтра":
        warnings.append("relative date needs human interpretation")
    if data.get("issue_type") == "other" and data.get("document_type"):
        warnings.append("document_type present but issue_type stayed other")
    return {
        "valid": not schema_errors and not missing_fields,
        "missing_fields": missing_fields,
        "schema_errors": schema_errors,
        "warnings": warnings,
    }

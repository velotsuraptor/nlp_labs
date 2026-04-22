from __future__ import annotations

import json
from copy import deepcopy
from typing import Any, Dict, List

SERVICE_ENUM: List[str] = [
    "єВідновлення",
    "Дія",
    "ЦНАП",
    "Паспортний сервіс",
    "Нотаріус",
    "Державний реєстр нерухомості",
    "Інша держпослуга",
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
    "consultation_or_advice",
    "other",
]

EXTRACTION_TASK = (
    "Extract structured support/admin-service attributes from a Ukrainian user message. "
    "The pipeline is designed for state-service and compensation-related texts."
)

NULL_RULES = {
    "document_type": "Use null when no concrete document or form is mentioned.",
    "date_text": "Use null when no explicit calendar date is mentioned.",
    "location_text": "Use null when no explicit place, city, office, or service point is mentioned.",
    "amounts_uah": "Use an empty list when no money amount is mentioned.",
}

SCHEMA: Dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "SupportAdminExtraction",
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


def get_extraction_schema() -> Dict[str, Any]:
    return deepcopy(SCHEMA)


def schema_as_markdown() -> str:
    lines = ["# Lab 11 extraction schema", "", f"Task: {EXTRACTION_TASK}", "", "## Fields"]
    for name, spec in SCHEMA["properties"].items():
        lines.append(f"- `{name}`: {json.dumps(spec, ensure_ascii=False)}")
    lines.extend([
        "",
        "## Required fields",
        "- " + ", ".join(f"`{name}`" for name in SCHEMA["required"]),
        "",
        "## Null / missing rules",
    ])
    for key, rule in NULL_RULES.items():
        lines.append(f"- `{key}`: {rule}")
    lines.extend(["", "## JSON schema", "```json", json.dumps(SCHEMA, ensure_ascii=False, indent=2), "```"])
    return "\n".join(lines)

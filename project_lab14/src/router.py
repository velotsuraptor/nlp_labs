"""
router.py — Keyword-based router for Lab 14 Flow Orchestration.
Classifies a cleaned text into one of the supported routes.
"""

import re

# ---------------------------------------------------------------------------
# Knowledge: known service keywords (lowercased fragments)
# ---------------------------------------------------------------------------
SERVICE_KEYWORDS = ["євіднов", "дія", "цнап", "паспорт", "нотаріус"]

MONEY_RE = re.compile(r"\d[\d\s]{0,10}\s*грн", re.IGNORECASE)

DOCUMENT_KEYWORDS = [
    "заяву", "заява", "документ", "паспорт", "свідоцтво",
    "довідку", "довідка", "витяг", "посвідчення",
]

ISSUE_KEYWORDS = [
    "не можу", "не надходить", "не надходила", "не знаходять",
    "помилка", "проблема", "відмова", "не працює", "не знайшли",
    "не пам'ятаю", "не пам'ятаєш", "не отримав", "не отримала",
    "компенсація", "повернути", "поверніть", "статус",
    "реєстрація", "черга", "запис", "кошти",
]

# ---------------------------------------------------------------------------
# Route registry
# ---------------------------------------------------------------------------
ROUTES: dict = {
    "support_extraction": {
        "schema": "support_schema",
        "required_fields": ["primary_service", "issue_type"],
    },
    "manual_review": {
        "schema": "manual_review_schema",
        "required_fields": [],
    },
}


def route(clean_text: str) -> dict:
    """
    Classify *clean_text* and return a routing decision dict.

    Returns
    -------
    dict with keys:
        route           – "support_extraction" | "manual_review"
        schema_name     – name of the matching schema
        required_fields – list of required fields for the chosen route
        routing_reason  – human-readable explanation
    """
    text = clean_text.strip().lower()

    # --- Empty / gibberish guard ---
    if not text or len(text) < 3:
        return _build(
            "manual_review",
            "Input is empty or too short for automated extraction.",
        )

    # Check for meaningful signal
    has_service_kw = any(kw in text for kw in SERVICE_KEYWORDS)
    has_money = bool(MONEY_RE.search(text))
    has_document_kw = any(kw in text for kw in DOCUMENT_KEYWORDS)
    has_issue_kw = any(kw in text for kw in ISSUE_KEYWORDS)

    signal_count = sum([has_service_kw, has_money, has_document_kw, has_issue_kw])

    if signal_count == 0:
        return _build(
            "manual_review",
            "No service, money, document, or issue keywords detected — likely gibberish or unrelated text.",
        )

    # Any signal → support_extraction
    reasons = []
    if has_service_kw:
        reasons.append("service keyword found")
    if has_money:
        reasons.append("money amount found")
    if has_document_kw:
        reasons.append("document keyword found")
    if has_issue_kw:
        reasons.append("issue keyword found")

    return _build("support_extraction", "; ".join(reasons))


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _build(route_name: str, reason: str) -> dict:
    route_cfg = ROUTES[route_name]
    return {
        "route": route_name,
        "schema_name": route_cfg["schema"],
        "required_fields": route_cfg["required_fields"],
        "routing_reason": reason,
    }

"""
fallback.py — Repair / graceful-degradation logic for Lab 14 Flow Orchestration.
Triggered when validation fails or execution errors occur.  Attempts rule-based
repair of the most common problems (missing primary_service).
"""

from typing import Any, Dict, List

try:
    from executor import SERVICE_ENUM
except ImportError:
    from src.executor import SERVICE_ENUM

# ---------------------------------------------------------------------------
# Service detection triggers (subset — for repair pass only)
# ---------------------------------------------------------------------------
_SERVICE_REPAIR_PATTERNS: List[tuple] = [
    ("єВідновлення", ["євідновлення", "євіднов"]),
    ("Дія", ["через дію", "дію", "дія"]),
    ("ЦНАП", ["цнап"]),
    ("Паспортний сервіс", ["паспортний сервіс", "паспорт"]),
    ("Нотаріус", ["нотаріус", "спадщин"]),
]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def fallback(route: str, clean_text: str, validation_result: dict) -> dict:
    """
    Attempt to repair failed extraction and return a fallback result dict.

    Returns
    -------
    dict with keys:
        fallback_type    – str describing what was tried
        repaired         – bool
        repaired_fields  – dict of fields that were successfully repaired
        reason           – human-readable explanation
        action           – "export_repaired" | "partial_export" | "safe_failure"
    """
    # --- Safe-failure routes (no repair possible) ---
    if route == "manual_review":
        return {
            "fallback_type": "no_repair_for_manual_review",
            "repaired": False,
            "repaired_fields": {},
            "reason": "Route 'manual_review' is not eligible for automated repair.",
            "action": "safe_failure",
        }

    # --- Identify what to repair ---
    issues = validation_result.get("issues", []) if validation_result else []
    problem_fields = {i["field"] for i in issues}
    warnings = validation_result.get("warnings", []) if validation_result else []

    text_lower = clean_text.lower()

    repaired_fields: Dict[str, Any] = {}

    # --- Attempt primary_service repair ---
    if "primary_service" in problem_fields or _service_is_missing_or_unknown(validation_result):
        detected: List[str] = []
        for canonical, triggers in _SERVICE_REPAIR_PATTERNS:
            if any(t in text_lower for t in triggers):
                detected.append(canonical)

        if len(detected) == 1:
            repaired_fields["primary_service"] = detected[0]
        elif len(detected) > 1:
            # Ambiguous — cannot repair deterministically
            pass

    # --- Decide outcome ---
    if repaired_fields:
        return {
            "fallback_type": "rule_based_service_repair",
            "repaired": True,
            "repaired_fields": repaired_fields,
            "reason": f"Repaired field(s): {list(repaired_fields.keys())}.",
            "action": "export_repaired",
        }

    # Repair failed
    reason_parts = []
    if problem_fields:
        reason_parts.append(f"Could not repair: {sorted(problem_fields)}.")
    if warnings:
        reason_parts.append("Unresolved warnings remain.")
    reason = " ".join(reason_parts) if reason_parts else "No repairable issues found."

    return {
        "fallback_type": "repair_failed",
        "repaired": False,
        "repaired_fields": {},
        "reason": reason,
        "action": "safe_failure",
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _service_is_missing_or_unknown(validation_result: dict) -> bool:
    """Return True if primary_service was 'unknown' or missing (from warnings)."""
    if not validation_result:
        return False
    warnings = validation_result.get("warnings", [])
    return any("primary_service" in w for w in warnings)

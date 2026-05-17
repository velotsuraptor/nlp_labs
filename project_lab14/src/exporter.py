"""
exporter.py — Export stage for Lab 14 Flow Orchestration.
Produces a clean, structured export dict from a completed FlowState.
"""

from typing import Any, Dict

# Fields that are internal metadata and should NOT appear in final_output
_INTERNAL_FIELDS = {"execution_method", "confidence"}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def export_result(state_dict: dict) -> dict:
    """
    Build the export payload from *state_dict* (FlowState.to_dict()).

    Returns
    -------
    dict with keys:
        case_id             – str
        route               – str
        final_output        – dict (execute_output minus internal fields)
        status              – str
        warnings            – list[str]
        errors              – list[str]
        needs_manual_review – bool
        fallback_triggered  – bool
    """
    execute_output: Dict[str, Any] = state_dict.get("execute_output") or {}
    fallback_result: Dict[str, Any] = state_dict.get("fallback_result") or {}
    repaired_fields: Dict[str, Any] = fallback_result.get("repaired_fields", {})

    # Merge repaired fields into the output
    merged_output = {**execute_output, **repaired_fields}

    # Strip internal fields
    final_output = {k: v for k, v in merged_output.items() if k not in _INTERNAL_FIELDS}

    status = state_dict.get("status", "unknown")
    fallback_triggered = state_dict.get("fallback_triggered", False)
    warnings = state_dict.get("warnings", [])
    errors = state_dict.get("errors", [])

    needs_manual_review = fallback_triggered or status == "safe_failure"

    return {
        "case_id": state_dict.get("case_id", ""),
        "route": state_dict.get("route", ""),
        "final_output": final_output if final_output else None,
        "status": status,
        "warnings": warnings,
        "errors": errors,
        "needs_manual_review": needs_manual_review,
        "fallback_triggered": fallback_triggered,
    }

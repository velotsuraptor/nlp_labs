"""
validator.py — Schema and field validator for Lab 14 Flow Orchestration.
Checks executor output against required fields and known enumerations,
and produces a structured validation report with actionable recommendations.
"""

from typing import Any, Dict, List

try:
    from executor import SERVICE_ENUM, ISSUE_ENUM
except ImportError:
    from src.executor import SERVICE_ENUM, ISSUE_ENUM


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def validate(route: str, execute_output: dict, required_fields: list) -> dict:
    """
    Validate *execute_output* for *route* against *required_fields*.

    Returns
    -------
    dict with keys:
        valid                – bool: no blocking issues
        schema_ok            – bool: all expected top-level keys present
        required_fields_ok   – bool: all required fields present and non-empty
        issues               – list[{field, problem}]
        warnings             – list[str]
        recommended_action   – "accept" | "export_with_warning" | "fallback" | "safe_failure"
    """
    if not execute_output:
        return _build(
            valid=False,
            schema_ok=False,
            required_fields_ok=False,
            issues=[{"field": "__all__", "problem": "execute_output is empty or None"}],
            warnings=[],
            recommended_action="safe_failure",
        )

    issues: List[Dict[str, str]] = []
    warnings: List[str] = []

    # --- Schema presence check ---
    expected_keys = {
        "primary_service", "services_mentioned", "issue_type",
        "document_type", "amounts_uah", "date_text", "location_text",
        "execution_method", "confidence",
    }
    if route == "support_extraction":
        missing_schema_keys = expected_keys - set(execute_output.keys())
        schema_ok = len(missing_schema_keys) == 0
        if not schema_ok:
            for k in sorted(missing_schema_keys):
                issues.append({"field": k, "problem": "key missing from execute_output"})
    else:
        schema_ok = True  # non-extraction routes have no strict schema

    # --- Required fields check ---
    required_fields_ok = True
    for f in required_fields:
        val = execute_output.get(f)
        if val is None or val == "" or val == []:
            issues.append({"field": f, "problem": "required field is missing or empty"})
            required_fields_ok = False
        elif f == "primary_service" and val == "unknown":
            # 'unknown' is a valid enum sentinel.
            # If services_mentioned is non-empty, the service is ambiguous (intentional unknown)
            # → treat as a warning, not a blocking issue.
            # If services_mentioned is empty, the service was genuinely not detected → blocking.
            services_mentioned = execute_output.get("services_mentioned", [])
            confidence = execute_output.get("confidence", "low")
            issue_type_val = execute_output.get("issue_type", "other")
            amounts = execute_output.get("amounts_uah", [])
            location = execute_output.get("location_text")
            date_val = execute_output.get("date_text")
            if not services_mentioned:
                # Genuinely no service found.
                # Allow export_with_warning only when there is at least one concrete extracted
                # value (amount, location, or date) AND issue_type is resolved.
                has_concrete_value = bool(amounts) or bool(location) or bool(date_val)
                # Also allow compensation/status issue types through with medium confidence
                # even without a concrete extracted value — the issue is the implicit signal.
                is_compensation_type = issue_type_val in ("payment_or_amount", "compensation_status")
                if issue_type_val != "other" and confidence in ("medium", "high") and (has_concrete_value or is_compensation_type):
                    pass  # non-blocking — falls through to warnings below
                else:
                    issues.append({
                        "field": f,
                        "problem": "primary_service resolved to 'unknown' — no service detected in text",
                    })
                    required_fields_ok = False
            # else: ambiguous but intentional — falls through to warnings below

    # --- Enum validation ---
    primary_service = execute_output.get("primary_service")
    if primary_service is not None and primary_service not in SERVICE_ENUM:
        issues.append({
            "field": "primary_service",
            "problem": f"value '{primary_service}' not in SERVICE_ENUM",
        })
        required_fields_ok = False

    issue_type = execute_output.get("issue_type")
    if issue_type is not None and issue_type not in ISSUE_ENUM:
        issues.append({
            "field": "issue_type",
            "problem": f"value '{issue_type}' not in ISSUE_ENUM",
        })
        required_fields_ok = False

    # --- Warnings (non-blocking) ---
    date_text = execute_output.get("date_text", "")
    if date_text and "завтра" in str(date_text).lower():
        warnings.append("date_text contains relative reference 'завтра' — may be ambiguous")

    if primary_service == "unknown":
        services_mentioned = execute_output.get("services_mentioned", [])
        if services_mentioned:
            warnings.append(
                "primary_service is 'unknown' despite services_mentioned being non-empty"
                f" ({services_mentioned}) — possible ambiguity"
            )
        else:
            warnings.append("primary_service is 'unknown' and no services were detected")

    confidence = execute_output.get("confidence", "high")
    if confidence == "low":
        warnings.append("extraction confidence is 'low' — result may be unreliable")
    elif confidence == "medium":
        warnings.append("extraction confidence is 'medium' — review recommended")

    # --- Recommended action ---
    valid = len(issues) == 0
    if not required_fields_ok:
        recommended_action = "fallback"
    elif not valid:
        recommended_action = "fallback"
    elif warnings:
        recommended_action = "export_with_warning"
    else:
        recommended_action = "accept"

    return _build(
        valid=valid,
        schema_ok=schema_ok,
        required_fields_ok=required_fields_ok,
        issues=issues,
        warnings=warnings,
        recommended_action=recommended_action,
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _build(
    valid: bool,
    schema_ok: bool,
    required_fields_ok: bool,
    issues: list,
    warnings: list,
    recommended_action: str,
) -> dict:
    return {
        "valid": valid,
        "schema_ok": schema_ok,
        "required_fields_ok": required_fields_ok,
        "issues": issues,
        "warnings": warnings,
        "recommended_action": recommended_action,
    }

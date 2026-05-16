from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

try:
    from .tool_logger import ToolCallLogger
    from .tools import classify_issue_type, extract_support_fields, validate_required_fields
except ImportError:  # pragma: no cover - notebook/path execution fallback
    from tool_logger import ToolCallLogger
    from tools import classify_issue_type, extract_support_fields, validate_required_fields


@dataclass
class BaselineSupportAssistant:
    """Weak single-pass baseline that does not call any tools."""

    def run(self, task_id: str, text: str) -> Dict[str, Any]:
        clean_text = text.lower()
        primary_service = "unknown"
        if "євіднов" in clean_text:
            primary_service = "єВідновлення"
        elif "дія" in clean_text:
            primary_service = "Дія"
        elif "цнап" in clean_text:
            primary_service = "ЦНАП"
        elif "паспорт" in clean_text:
            primary_service = "Паспортний сервіс"
        elif "нотаріус" in clean_text:
            primary_service = "Нотаріус"

        issue_type = "other"
        if "заяв" in clean_text:
            issue_type = "application_submission"
        elif "документ" in clean_text or "довідк" in clean_text:
            issue_type = "document_requirement"
        elif "грн" in clean_text:
            issue_type = "payment_or_amount"
        elif "черг" in clean_text:
            issue_type = "registration_or_queue"
        elif "не можу" in clean_text:
            issue_type = "service_access_problem"

        extraction = {
            "primary_service": primary_service,
            "services_mentioned": [primary_service] if primary_service != "unknown" else [],
            "issue_type": issue_type,
            "document_type": "заява" if "заяв" in clean_text else None,
            "amounts_uah": [],
            "date_text": None,
            "location_text": None,
        }
        route = "generic_route" if issue_type == "other" else f"{issue_type}_route"
        return {
            "task_id": task_id,
            "route": route,
            "used_tools": [],
            "needs_manual_check": issue_type == "other",
            "final_output": extraction,
            "final_answer": f"Baseline guessed issue_type={issue_type} and primary_service={primary_service}.",
        }


@dataclass
class ToolGroundedSupportAgent:
    """Single agent that decides when to call tools and builds a final routed answer."""

    logger: ToolCallLogger

    def _should_validate(
        self,
        classification: Dict[str, Any],
        extraction: Dict[str, Any],
    ) -> tuple[bool, str | None, bool]:
        if classification.get("ambiguous"):
            return True, "ambiguous service or routing", False
        if classification.get("noisy"):
            return True, "noisy text requires structure check", False
        if (
            classification.get("issue_type") == "payment_or_amount"
            and extraction.get("document_type") == "паспорт"
        ):
            return True, "low_risk_double_check", True
        if classification.get("issue_type") in {"document_requirement", "payment_or_amount"}:
            return True, "high-value fields need validation", False
        if classification.get("issue_type") == "registration_or_queue" and extraction.get("amounts_uah"):
            return True, "low_risk_double_check", True
        return False, None, False

    def run(self, task_id: str, text: str) -> Dict[str, Any]:
        classification = self.logger.call(
            task_id,
            "classify_issue_type",
            classify_issue_type,
            reason="decide route and whether later validation is needed",
            text=text,
        )
        extraction = self.logger.call(
            task_id,
            "extract_support_fields",
            extract_support_fields,
            reason="build structured support extraction",
            text=text,
        )

        validation = None
        should_validate, reason, unnecessary = self._should_validate(classification, extraction)
        if should_validate:
            validation = self.logger.call(
                task_id,
                "validate_required_fields",
                validate_required_fields,
                reason=reason,
                metadata={"unnecessary": unnecessary},
                data=extraction,
            )

        needs_manual_check = False
        status = "accepted"
        notes: List[str] = []
        if validation:
            notes.extend(validation.get("warnings", []))
            if not validation.get("valid", False):
                needs_manual_check = True
                status = "needs_manual_check"
                notes.extend(validation.get("missing_fields", []))
                notes.extend(validation.get("schema_errors", []))
        if classification.get("ambiguous") and extraction.get("primary_service") == "unknown":
            needs_manual_check = True
            status = "needs_manual_check"
            notes.append("ambiguous service mention")

        route = classification.get("route_hint", "generic_route")
        final_answer = (
            f"Route: {route}. issue_type={extraction['issue_type']}; "
            f"primary_service={extraction['primary_service']}; "
            f"services={extraction['services_mentioned']}; "
            f"amounts={extraction['amounts_uah']}; "
            f"date={extraction['date_text']}; location={extraction['location_text']}."
        )
        if notes:
            final_answer += " Notes: " + "; ".join(sorted(set(str(note) for note in notes))) + "."

        used_tools = ["classify_issue_type", "extract_support_fields"]
        if validation is not None:
            used_tools.append("validate_required_fields")
        return {
            "task_id": task_id,
            "route": route,
            "used_tools": used_tools,
            "needs_manual_check": needs_manual_check,
            "status": status,
            "classification": classification,
            "validation": validation,
            "final_output": extraction,
            "final_answer": final_answer,
        }

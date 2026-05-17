"""
flow_state.py — FlowState dataclass for Lab 14 Flow Orchestration.
Tracks all intermediate results as a message moves through the pipeline stages:
ingest → route → execute → validate → (fallback) → export.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class FlowState:
    """Single case state container passed through all pipeline stages."""

    # --- Identity ---
    case_id: str = ""
    raw_text: str = ""
    clean_text: str = ""

    # --- Routing ---
    route: str = ""
    schema_name: str = ""
    routing_reason: str = ""

    # --- Stage outputs ---
    execute_output: Optional[Dict[str, Any]] = None
    validation_result: Optional[Dict[str, Any]] = None
    fallback_result: Optional[Dict[str, Any]] = None
    final_output: Optional[Dict[str, Any]] = None

    # --- Flow control ---
    status: str = "pending"
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    steps: List[Dict[str, Any]] = field(default_factory=list)
    fallback_triggered: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Return all fields as a plain dict (serialisation helper)."""
        return {
            "case_id": self.case_id,
            "raw_text": self.raw_text,
            "clean_text": self.clean_text,
            "route": self.route,
            "schema_name": self.schema_name,
            "routing_reason": self.routing_reason,
            "execute_output": self.execute_output,
            "validation_result": self.validation_result,
            "fallback_result": self.fallback_result,
            "final_output": self.final_output,
            "status": self.status,
            "errors": self.errors,
            "warnings": self.warnings,
            "steps": self.steps,
            "fallback_triggered": self.fallback_triggered,
        }

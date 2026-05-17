"""
flow_logger.py — Structured JSONL logger for Lab 14 Flow Orchestration.
Records every case that passes through SupportExtractionFlow so that
runs can be audited and metrics can be computed post-hoc.
"""

import json
import pathlib
from typing import Any, Dict, List


class FlowLogger:
    """Accumulate flow records in memory and persist them to JSONL."""

    def __init__(self) -> None:
        self.records: List[Dict[str, Any]] = []

    def log_case(self, state_dict: dict, export_output: dict) -> None:
        """
        Append a log record combining the full state snapshot and the
        export payload.

        Parameters
        ----------
        state_dict   : FlowState.to_dict() snapshot taken after export
        export_output: result of exporter.export_result(state_dict)
        """
        record = {
            "case_id": state_dict.get("case_id", ""),
            "input": state_dict.get("raw_text", ""),
            "route": state_dict.get("route", ""),
            "steps": state_dict.get("steps", []),
            "validation_result": state_dict.get("validation_result"),
            "fallback_triggered": state_dict.get("fallback_triggered", False),
            "fallback_result": state_dict.get("fallback_result"),
            "export_output": export_output,
            "final_status": state_dict.get("status", "unknown"),
            "errors": state_dict.get("errors", []),
            "warnings": state_dict.get("warnings", []),
        }
        self.records.append(record)

    def save_jsonl(self, path: str) -> None:
        """
        Write all accumulated records to *path* as newline-delimited JSON.
        Creates parent directories if they do not exist.
        """
        p = pathlib.Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as fh:
            for record in self.records:
                fh.write(json.dumps(record, ensure_ascii=False) + "\n")

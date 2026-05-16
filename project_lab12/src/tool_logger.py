from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


@dataclass
class ToolCallLogger:
    """Structured logger for every tool call made by the single-agent pipeline."""

    records: List[Dict[str, Any]] = field(default_factory=list)

    def call(
        self,
        task_id: str,
        tool_name: str,
        tool_func: Callable[..., Any],
        reason: str | None = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        timestamp = datetime.now(timezone.utc).isoformat()
        try:
            output = tool_func(**kwargs)
            record = {
                "timestamp": timestamp,
                "task_id": task_id,
                "tool_name": tool_name,
                "input": kwargs,
                "output": output,
                "success": True,
                "error": None,
                "reason": reason,
                "metadata": metadata or {},
            }
            self.records.append(record)
            return output
        except Exception as exc:  # pragma: no cover
            record = {
                "timestamp": timestamp,
                "task_id": task_id,
                "tool_name": tool_name,
                "input": kwargs,
                "output": None,
                "success": False,
                "error": str(exc),
                "reason": reason,
                "metadata": metadata or {},
            }
            self.records.append(record)
            return {"error": str(exc)}

    def save_jsonl(self, path: str | Path) -> None:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("w", encoding="utf-8") as handle:
            for record in self.records:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    def records_for_task(self, task_id: str) -> List[Dict[str, Any]]:
        return [record for record in self.records if record["task_id"] == task_id]

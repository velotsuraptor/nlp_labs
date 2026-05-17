"""
flow.py — SupportExtractionFlow: the top-level orchestrator for Lab 14.
Implements the five-stage pipeline:
    ingest → route → execute → validate → (fallback) → export
and records every transition in FlowState.steps.
"""

try:
    from flow_state import FlowState
    from router import route as _route, ROUTES
    from executor import execute as _execute, normalize
    from validator import validate as _validate
    from fallback import fallback as _fallback
    from exporter import export_result
    from flow_logger import FlowLogger
except ImportError:
    from src.flow_state import FlowState
    from src.router import route as _route, ROUTES
    from src.executor import execute as _execute, normalize
    from src.validator import validate as _validate
    from src.fallback import fallback as _fallback
    from src.exporter import export_result
    from src.flow_logger import FlowLogger


class SupportExtractionFlow:
    """Stateful five-stage extraction flow for Ukrainian admin-service messages."""

    def __init__(self) -> None:
        self.logger = FlowLogger()

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def run(self, case_id: str, text: str) -> dict:
        """
        Process a single message and return the export payload dict.

        Parameters
        ----------
        case_id : unique identifier for this case
        text    : raw input text from the user

        Returns
        -------
        export payload as produced by exporter.export_result()
        """
        state = FlowState(case_id=case_id)

        # ── Stage 1: Ingest ──────────────────────────────────────────
        state = self._ingest(state, text)
        if state.status in ("safe_failure",):
            return self._export(state)

        # ── Stage 2: Route ───────────────────────────────────────────
        state = self._route_stage(state)
        if state.status == "safe_failure" or state.fallback_triggered:
            return self._export(state)

        # ── Stage 3: Execute ─────────────────────────────────────────
        state = self._execute_stage(state)
        if state.status == "execute_failed":
            state = self._fallback_stage(state)
            return self._export(state)

        # ── Stage 4: Validate ────────────────────────────────────────
        state = self._validate_stage(state)
        if state.status == "validation_failed":
            state = self._fallback_stage(state)
            return self._export(state)

        # ── Stage 5: Export (happy path) ─────────────────────────────
        return self._export(state)

    # ------------------------------------------------------------------
    # Stage implementations
    # ------------------------------------------------------------------

    def _ingest(self, state: FlowState, text: str) -> FlowState:
        state.raw_text = text
        state.clean_text = normalize(text)

        if not state.clean_text.strip():
            state.errors.append("Input text is empty after normalisation.")
            state.status = "safe_failure"
            state.steps.append({
                "step": "ingest",
                "status": "error",
                "detail": "empty input",
            })
        else:
            state.status = "ingested"
            state.steps.append({
                "step": "ingest",
                "status": "ok",
                "clean_text_length": len(state.clean_text),
            })
        return state

    def _route_stage(self, state: FlowState) -> FlowState:
        routing = _route(state.clean_text)
        state.route = routing["route"]
        state.schema_name = routing["schema_name"]
        state.routing_reason = routing["routing_reason"]

        if state.route == "manual_review":
            state.fallback_triggered = True
            state.status = "safe_failure"
            state.warnings.append(f"Routed to manual_review: {state.routing_reason}")
            state.steps.append({
                "step": "route",
                "status": "warning",
                "route": state.route,
                "reason": state.routing_reason,
            })
        else:
            state.steps.append({
                "step": "route",
                "status": "ok",
                "route": state.route,
                "schema": state.schema_name,
                "reason": state.routing_reason,
            })
        return state

    def _execute_stage(self, state: FlowState) -> FlowState:
        try:
            result = _execute(state.route, state.clean_text)
            state.execute_output = result
            state.steps.append({
                "step": "execute",
                "status": "ok",
                "primary_service": result.get("primary_service"),
                "issue_type": result.get("issue_type"),
                "confidence": result.get("confidence"),
            })
        except Exception as exc:  # noqa: BLE001
            state.errors.append(f"Execute stage exception: {exc}")
            state.status = "execute_failed"
            state.steps.append({
                "step": "execute",
                "status": "error",
                "error": str(exc),
            })
        return state

    def _validate_stage(self, state: FlowState) -> FlowState:
        required = ROUTES.get(state.route, {}).get("required_fields", [])
        vr = _validate(state.route, state.execute_output or {}, required)
        state.validation_result = vr

        # Propagate warnings
        for w in vr.get("warnings", []):
            if w not in state.warnings:
                state.warnings.append(w)

        if not vr["valid"] or vr["recommended_action"] in ("fallback", "safe_failure"):
            state.status = "validation_failed"
            state.fallback_triggered = True
            state.steps.append({
                "step": "validate",
                "status": "error",
                "issues": vr["issues"],
                "recommended_action": vr["recommended_action"],
            })
        else:
            state.steps.append({
                "step": "validate",
                "status": "ok" if not vr["warnings"] else "warning",
                "warnings": vr["warnings"],
                "recommended_action": vr["recommended_action"],
            })
        return state

    def _fallback_stage(self, state: FlowState) -> FlowState:
        fb = _fallback(state.route, state.clean_text, state.validation_result or {})
        state.fallback_result = fb

        if fb["repaired"]:
            # Merge repaired fields
            if state.execute_output is None:
                state.execute_output = {}
            state.execute_output.update(fb["repaired_fields"])
            state.status = "fallback_repaired"
            state.steps.append({
                "step": "fallback",
                "status": "ok",
                "repaired_fields": list(fb["repaired_fields"].keys()),
                "action": fb["action"],
            })
        else:
            action = fb.get("action", "safe_failure")
            state.status = "safe_failure" if action == "safe_failure" else "partial_export"
            state.steps.append({
                "step": "fallback",
                "status": "error",
                "reason": fb["reason"],
                "action": action,
            })
        return state

    def _export(self, state: FlowState) -> dict:
        # Resolve final status label
        if state.status not in ("safe_failure", "partial_export", "fallback_repaired"):
            vr = state.validation_result or {}
            if vr.get("warnings"):
                state.status = "exported_with_warning"
            elif state.status == "ingested":
                # Passed all stages cleanly
                state.status = "exported"
            else:
                state.status = "exported"

        state.steps.append({
            "step": "export",
            "status": "ok",
            "final_status": state.status,
        })

        export_output = export_result(state.to_dict())
        state.final_output = export_output.get("final_output")

        self.logger.log_case(state.to_dict(), export_output)
        return export_output

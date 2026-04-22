from __future__ import annotations

from dataclasses import dataclass

from validator import ValidationResult, validate_output


@dataclass
class RepairRecord:
    text_id: int
    text: str
    raw_output: str
    raw_validation: ValidationResult
    final_output: str
    final_validation: ValidationResult
    repairs_used: int
    repair_needed: bool


def run_repair_loop(text_id: int, text: str, client, schema, max_repairs: int = 2) -> RepairRecord:
    raw_output = client.extract(text)
    raw_validation = validate_output(raw_output, schema)
    current_output = raw_output
    current_validation = raw_validation
    repairs_used = 0
    while repairs_used < max_repairs and not current_validation.schema_ok:
        repairs_used += 1
        validation_error = current_validation.error_message or 'unknown validation error'
        current_output = client.repair(text, current_output, validation_error)
        current_validation = validate_output(current_output, schema)
        if current_validation.schema_ok:
            break
    return RepairRecord(text_id=text_id, text=text, raw_output=raw_output, raw_validation=raw_validation, final_output=current_output, final_validation=current_validation, repairs_used=repairs_used, repair_needed=not raw_validation.schema_ok)

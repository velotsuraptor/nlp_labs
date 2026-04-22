from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from jsonschema import Draft202012Validator


@dataclass
class ValidationResult:
    raw_text: str
    parsed: Optional[Dict[str, Any]]
    parse_ok: bool
    schema_ok: bool
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    schema_errors: List[str] = field(default_factory=list)


def validate_output(raw_text: str, schema: Dict[str, Any]) -> ValidationResult:
    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        return ValidationResult(raw_text=raw_text, parsed=None, parse_ok=False, schema_ok=False, error_type='json_parse_error', error_message=str(exc))
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(parsed), key=lambda err: list(err.absolute_path))
    if not errors:
        return ValidationResult(raw_text=raw_text, parsed=parsed, parse_ok=True, schema_ok=True)
    first = errors[0]
    path = '.'.join(str(part) for part in first.absolute_path) or '<root>'
    error_type = 'schema_violation'
    if 'is a required property' in first.message:
        error_type = 'missing_required_field'
    elif 'is not of type' in first.message:
        error_type = 'wrong_field_type'
    elif 'Additional properties are not allowed' in first.message:
        error_type = 'hallucinated_field'
    return ValidationResult(raw_text=raw_text, parsed=parsed, parse_ok=True, schema_ok=False, error_type=error_type, error_message=f'{path}: {first.message}', schema_errors=[f"{'.'.join(str(part) for part in err.absolute_path) or '<root>'}: {err.message}" for err in errors])

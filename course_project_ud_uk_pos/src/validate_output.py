from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ALLOWED_UPOS = {
    "ADJ",
    "ADP",
    "ADV",
    "AUX",
    "CCONJ",
    "DET",
    "INTJ",
    "NOUN",
    "NUM",
    "PART",
    "PRON",
    "PROPN",
    "PUNCT",
    "SCONJ",
    "SYM",
    "VERB",
    "X",
}


def validate_prediction(obj: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(obj, dict):
        return ["root is not an object"]

    for key in ("sentence_id", "text", "tokens"):
        if key not in obj:
            errors.append(f"missing key: {key}")

    tokens = obj.get("tokens")
    if not isinstance(tokens, list):
        errors.append("tokens must be a list")
        return errors

    for i, token in enumerate(tokens, start=1):
        if not isinstance(token, dict):
            errors.append(f"tokens[{i}] is not an object")
            continue
        for key in ("id", "form", "upos_pred", "feats_pred"):
            if key not in token:
                errors.append(f"tokens[{i}] missing key: {key}")
        upos = token.get("upos_pred")
        if isinstance(upos, str) and upos not in ALLOWED_UPOS:
            errors.append(f"tokens[{i}] invalid upos_pred: {upos}")
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate prediction JSON output.")
    parser.add_argument("--input-json", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    obj = json.loads(args.input_json.read_text(encoding="utf-8"))
    errors = validate_prediction(obj)
    if errors:
        print("INVALID")
        for err in errors:
            print(f"- {err}")
        raise SystemExit(1)
    print("VALID")


if __name__ == "__main__":
    main()


from __future__ import annotations

import argparse
import json
import pickle
import sys
from pathlib import Path
from typing import Any

# Ensure project root is on sys.path when running as a script.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.predict import build_sentence, predict_with_crf
from src.validate_output import validate_prediction


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run regression checks on fixed inference cases.")
    parser.add_argument("--model-path", type=Path, default=Path("models/crf_upos.pkl"))
    parser.add_argument("--cases-path", type=Path, default=Path("tests/regression_cases.jsonl"))
    parser.add_argument("--out-path", type=Path, default=Path("outputs/regression_results.json"))
    return parser.parse_args()


def load_model(path: Path) -> Any:
    with path.open("rb") as handle:
        return pickle.load(handle)


def load_cases(path: Path) -> list[dict[str, str]]:
    cases: list[dict[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        cases.append(json.loads(stripped))
    return cases


def main() -> None:
    args = parse_args()
    model = load_model(args.model_path)
    cases = load_cases(args.cases_path)

    total = 0
    valid = 0
    failed_cases: list[dict[str, Any]] = []
    for row in cases:
        total += 1
        text = row["text"]
        sentence = build_sentence(text)
        prediction = predict_with_crf(model, sentence)
        errors = validate_prediction(prediction)
        if errors:
            failed_cases.append({"text": text, "errors": errors})
        else:
            valid += 1

    result = {
        "total_cases": total,
        "valid_cases": valid,
        "failed_cases": len(failed_cases),
        "pass_rate": round(valid / total, 6) if total else 0.0,
        "failures": failed_cases,
    }
    args.out_path.parent.mkdir(parents=True, exist_ok=True)
    args.out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if failed_cases:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

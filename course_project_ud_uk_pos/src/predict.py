from __future__ import annotations

import argparse
import json
import pickle
import re
import sys
from pathlib import Path
from typing import Any

from src.features import split_joint_label, token_to_features


TOKEN_PATTERN = re.compile(r"\w+|[^\w\s]", flags=re.UNICODE)


def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text)


def build_sentence(text: str) -> dict[str, Any]:
    tokens = tokenize(text)
    return {
        "sentence_id": "inference_0001",
        "text": text,
        "tokens": [{"id": i + 1, "form": token} for i, token in enumerate(tokens)],
    }


def load_model(path: Path) -> Any:
    with path.open("rb") as handle:
        return pickle.load(handle)


def load_fallback_model(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    with path.open("rb") as handle:
        model = pickle.load(handle)
    if not isinstance(model, dict):
        return None
    if "lexicon" in model and "fallback_label" in model:
        return {"type": "lexicon", **model}
    if "majority_label" in model:
        return {"type": "majority", **model}
    return None


def predict_with_fallback(sentence: dict[str, Any], fallback_model: dict[str, Any]) -> dict[str, Any]:
    output_tokens = []
    model_type = fallback_model["type"]
    for token in sentence["tokens"]:
        form = token["form"]
        if model_type == "lexicon":
            label = fallback_model["lexicon"].get(form.lower(), fallback_model["fallback_label"])
        else:
            label = fallback_model["majority_label"]
        upos, feats = split_joint_label(label)
        output_tokens.append(
            {
                "id": token["id"],
                "form": token["form"],
                "upos_pred": upos,
                "feats_pred": feats,
            }
        )

    return {
        "sentence_id": sentence["sentence_id"],
        "text": sentence["text"],
        "tokens": output_tokens,
    }


def predict_with_crf(model: Any, sentence: dict[str, Any]) -> dict[str, Any]:
    x_seq = [token_to_features(sentence["tokens"], i) for i in range(len(sentence["tokens"]))]
    labels = model.predict_single(x_seq)

    output_tokens = []
    for token, label in zip(sentence["tokens"], labels):
        upos, feats = split_joint_label(label)
        output_tokens.append(
            {
                "id": token["id"],
                "form": token["form"],
                "upos_pred": upos,
                "feats_pred": feats,
            }
        )

    return {
        "sentence_id": sentence["sentence_id"],
        "text": sentence["text"],
        "tokens": output_tokens,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Predict tags for a raw Ukrainian sentence.")
    parser.add_argument("--model-path", type=Path, required=True)
    parser.add_argument("--fallback-model-path", type=Path, default=None)
    parser.add_argument("--text", type=str, required=True)
    return parser.parse_args()


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    args = parse_args()
    sentence = build_sentence(args.text)
    fallback_model = load_fallback_model(args.fallback_model_path)

    try:
        model = load_model(args.model_path)
        prediction = predict_with_crf(model, sentence)
    except Exception:
        if fallback_model is None:
            raise
        prediction = predict_with_fallback(sentence, fallback_model)

    print(json.dumps(prediction, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

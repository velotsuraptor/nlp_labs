from __future__ import annotations

import argparse
import pickle
from pathlib import Path
from typing import Any

import jsonlines
from sklearn_crfsuite import CRF

from src.evaluate import compute_metrics, save_confusion_matrix, save_error_cases, save_metrics
from src.features import sentence_to_xy


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with jsonlines.open(path, mode="r") as reader:
        return list(reader)


def build_xy(sentences: list[dict[str, Any]], label_field: str) -> tuple[list[list[dict[str, Any]]], list[list[str]]]:
    x_all: list[list[dict[str, Any]]] = []
    y_all: list[list[str]] = []
    for sentence in sentences:
        x_seq, y_seq = sentence_to_xy(sentence, label_field=label_field)
        x_all.append(x_seq)
        y_all.append(y_seq)
    return x_all, y_all


def save_pickle(obj: Any, path: Path) -> None:
    with path.open("wb") as handle:
        pickle.dump(obj, handle)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a CRF POS tagger.")
    parser.add_argument("--processed-dir", type=Path, default=Path("data/processed"))
    parser.add_argument("--models-dir", type=Path, default=Path("models"))
    parser.add_argument("--outputs-dir", type=Path, default=Path("outputs"))
    parser.add_argument("--label-field", choices=("upos", "joint"), default="upos")
    parser.add_argument("--c1", type=float, default=0.1)
    parser.add_argument("--c2", type=float, default=0.1)
    parser.add_argument("--max-iterations", type=int, default=200)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ensure_dir(args.models_dir)
    ensure_dir(args.outputs_dir)

    train_sentences = load_jsonl(args.processed_dir / "train.jsonl")
    dev_sentences = load_jsonl(args.processed_dir / "dev.jsonl")
    test_sentences = load_jsonl(args.processed_dir / "test.jsonl")

    x_train, y_train = build_xy(train_sentences, label_field=args.label_field)
    x_dev, y_dev = build_xy(dev_sentences, label_field=args.label_field)
    x_test, y_test = build_xy(test_sentences, label_field=args.label_field)

    model = CRF(
        algorithm="lbfgs",
        c1=args.c1,
        c2=args.c2,
        max_iterations=args.max_iterations,
        all_possible_transitions=True,
    )
    model.fit(x_train, y_train)

    y_dev_pred = model.predict(x_dev)
    y_test_pred = model.predict(x_test)

    metrics = {
        "config": {
            "label_field": args.label_field,
            "c1": args.c1,
            "c2": args.c2,
            "max_iterations": args.max_iterations,
        },
        "dev": compute_metrics(y_dev, y_dev_pred),
        "test": compute_metrics(y_test, y_test_pred),
    }

    model_path = args.models_dir / f"crf_{args.label_field}.pkl"
    save_pickle(model, model_path)

    metrics_path = args.outputs_dir / f"crf_{args.label_field}_metrics.json"
    save_metrics(metrics, metrics_path)

    if args.label_field == "upos":
        confusion_path = args.outputs_dir / "crf_upos_confusion_matrix.png"
        save_confusion_matrix(y_test, y_test_pred, confusion_path, title="CRF POS Tagging Confusion Matrix")

    error_path = args.outputs_dir / f"error_cases_crf_{args.label_field}.jsonl"
    save_error_cases(test_sentences, y_test, y_test_pred, error_path, limit=100)

    print(f"Saved model: {model_path}")
    print(f"Saved metrics: {metrics_path}")
    print(f"Saved errors: {error_path}")


if __name__ == "__main__":
    main()


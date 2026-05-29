from __future__ import annotations

import argparse
import pickle
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import jsonlines

from src.evaluate import compute_metrics, save_metrics
from src.features import make_label


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with jsonlines.open(path, mode="r") as reader:
        return list(reader)


def labels_from_sentences(sentences: list[dict[str, Any]], label_field: str) -> list[list[str]]:
    return [[make_label(token, label_field=label_field) for token in sentence["tokens"]] for sentence in sentences]


def forms_from_sentences(sentences: list[dict[str, Any]]) -> list[list[str]]:
    return [[token["form"] for token in sentence["tokens"]] for sentence in sentences]


def train_majority_baseline(train_sentences: list[dict[str, Any]], label_field: str) -> dict[str, Any]:
    counter = Counter(label for seq in labels_from_sentences(train_sentences, label_field=label_field) for label in seq)
    majority_label = counter.most_common(1)[0][0]
    return {"majority_label": majority_label, "label_field": label_field}


def predict_majority(model: dict[str, Any], form_sequences: list[list[str]]) -> list[list[str]]:
    label = model["majority_label"]
    return [[label for _ in sequence] for sequence in form_sequences]


def train_lexicon_baseline(train_sentences: list[dict[str, Any]], label_field: str) -> dict[str, Any]:
    label_counts_by_form: dict[str, Counter] = defaultdict(Counter)
    global_counts = Counter()

    for sentence in train_sentences:
        for token in sentence["tokens"]:
            form = token["form"].lower()
            label = make_label(token, label_field=label_field)
            label_counts_by_form[form][label] += 1
            global_counts[label] += 1

    lexicon = {form: counts.most_common(1)[0][0] for form, counts in label_counts_by_form.items()}
    majority_label = global_counts.most_common(1)[0][0]
    return {
        "lexicon": lexicon,
        "fallback_label": majority_label,
        "label_field": label_field,
    }


def predict_lexicon(model: dict[str, Any], form_sequences: list[list[str]]) -> list[list[str]]:
    lexicon = model["lexicon"]
    fallback = model["fallback_label"]
    return [[lexicon.get(form.lower(), fallback) for form in sequence] for sequence in form_sequences]


def save_pickle(obj: Any, path: Path) -> None:
    with path.open("wb") as handle:
        pickle.dump(obj, handle)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train majority and lexicon baselines.")
    parser.add_argument("--processed-dir", type=Path, default=Path("data/processed"))
    parser.add_argument("--models-dir", type=Path, default=Path("models"))
    parser.add_argument("--outputs-dir", type=Path, default=Path("outputs"))
    parser.add_argument("--label-field", choices=("upos", "joint"), default="upos")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ensure_dir(args.models_dir)
    ensure_dir(args.outputs_dir)

    train_sentences = load_jsonl(args.processed_dir / "train.jsonl")
    dev_sentences = load_jsonl(args.processed_dir / "dev.jsonl")
    test_sentences = load_jsonl(args.processed_dir / "test.jsonl")

    splits = {
        "dev": dev_sentences,
        "test": test_sentences,
    }

    form_sequences = {name: forms_from_sentences(sentences) for name, sentences in splits.items()}
    gold_labels = {name: labels_from_sentences(sentences, label_field=args.label_field) for name, sentences in splits.items()}

    majority_model = train_majority_baseline(train_sentences, label_field=args.label_field)
    lexicon_model = train_lexicon_baseline(train_sentences, label_field=args.label_field)

    save_pickle(majority_model, args.models_dir / f"baseline_majority_{args.label_field}.pkl")
    save_pickle(lexicon_model, args.models_dir / f"baseline_lexicon_{args.label_field}.pkl")

    metrics = {}
    for model_name, model, predictor in (
        ("majority", majority_model, predict_majority),
        ("lexicon", lexicon_model, predict_lexicon),
    ):
        metrics[model_name] = {}
        for split_name in ("dev", "test"):
            y_pred = predictor(model, form_sequences[split_name])
            metrics[model_name][split_name] = compute_metrics(gold_labels[split_name], y_pred)

    metrics_path = args.outputs_dir / f"baseline_{args.label_field}_metrics.json"
    save_metrics(metrics, metrics_path)
    print(f"Saved baseline models and metrics to {metrics_path}")


if __name__ == "__main__":
    main()


from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonlines
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score

from src.features import split_joint_label


def flatten(sequences: list[list[str]]) -> list[str]:
    return [item for sequence in sequences for item in sequence]


def sequence_exact_match(y_true: list[list[str]], y_pred: list[list[str]]) -> float:
    if not y_true:
        return 0.0
    correct = sum(1 for gold, pred in zip(y_true, y_pred) if gold == pred)
    return correct / len(y_true)


def compute_metrics(y_true: list[list[str]], y_pred: list[list[str]]) -> dict[str, Any]:
    gold_flat = flatten(y_true)
    pred_flat = flatten(y_pred)
    labels = sorted(set(gold_flat) | set(pred_flat))
    report = classification_report(gold_flat, pred_flat, labels=labels, output_dict=True, zero_division=0)
    return {
        "token_accuracy": accuracy_score(gold_flat, pred_flat),
        "macro_f1": f1_score(gold_flat, pred_flat, average="macro", zero_division=0),
        "weighted_f1": f1_score(gold_flat, pred_flat, average="weighted", zero_division=0),
        "sequence_exact_match": sequence_exact_match(y_true, y_pred),
        "labels": labels,
        "classification_report": report,
    }


def save_metrics(metrics: dict[str, Any], path: Path) -> None:
    path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")


def save_confusion_matrix(y_true: list[list[str]], y_pred: list[list[str]], path: Path, title: str) -> None:
    gold_flat = flatten(y_true)
    pred_flat = flatten(y_pred)
    labels = sorted(set(gold_flat) | set(pred_flat))
    matrix = confusion_matrix(gold_flat, pred_flat, labels=labels)

    plt.figure(figsize=(10, 8))
    sns.heatmap(matrix, xticklabels=labels, yticklabels=labels, cmap="Blues", annot=False)
    plt.title(title)
    plt.xlabel("Predicted")
    plt.ylabel("Gold")
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()


def save_error_cases(
    sentences: list[dict[str, Any]],
    y_true: list[list[str]],
    y_pred: list[list[str]],
    path: Path,
    limit: int = 100,
) -> None:
    num_saved = 0
    with jsonlines.open(path, mode="w") as writer:
        for sentence, gold_seq, pred_seq in zip(sentences, y_true, y_pred):
            mismatches = []
            for token, gold, pred in zip(sentence["tokens"], gold_seq, pred_seq):
                if gold == pred:
                    continue
                gold_upos, gold_feats = split_joint_label(gold)
                pred_upos, pred_feats = split_joint_label(pred)
                mismatches.append(
                    {
                        "token_id": token["id"],
                        "form": token["form"],
                        "gold_label": gold,
                        "pred_label": pred,
                        "gold_upos": gold_upos,
                        "pred_upos": pred_upos,
                        "gold_feats": gold_feats,
                        "pred_feats": pred_feats,
                    }
                )

            if mismatches:
                writer.write(
                    {
                        "sentence_id": sentence["sentence_id"],
                        "text": sentence["text"],
                        "mismatches": mismatches,
                    }
                )
                num_saved += 1
                if num_saved >= limit:
                    break

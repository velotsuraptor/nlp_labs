from __future__ import annotations

from typing import Dict, Iterable, List

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, f1_score, precision_recall_curve, precision_score, recall_score


def one_vs_rest_scores(pipe, texts: Iterable[str], positive_class: str) -> np.ndarray:
    clf = pipe.named_steps["clf"]
    features = pipe.named_steps["features"] if "features" in pipe.named_steps else pipe.named_steps["tfidf"]
    x = features.transform(pd.Series(list(texts)).astype(str))
    scores = clf.decision_function(x)
    classes = list(clf.classes_)

    if scores.ndim == 1:
        if classes[1] != positive_class:
            scores = -scores
        return scores

    pos_idx = classes.index(positive_class)
    return scores[:, pos_idx]


def precision_recall_summary(y_true_binary: np.ndarray, scores: np.ndarray) -> Dict:
    precision, recall, thresholds = precision_recall_curve(y_true_binary, scores)
    ap = float(average_precision_score(y_true_binary, scores))
    return {
        "precision": precision,
        "recall": recall,
        "thresholds": thresholds,
        "average_precision": ap,
    }


def plot_pr_curve(y_true_binary: np.ndarray, scores: np.ndarray) -> pd.DataFrame:
    summary = precision_recall_summary(y_true_binary, scores)
    precision = summary["precision"]
    recall = summary["recall"]
    thresholds = summary["thresholds"]

    rows: List[Dict] = []
    for idx in range(len(thresholds)):
        rows.append(
            {
                "threshold": float(thresholds[idx]),
                "precision": float(precision[idx + 1]),
                "recall": float(recall[idx + 1]),
            }
        )
    return pd.DataFrame(rows)


def evaluate_thresholds(y_true_binary: np.ndarray, scores: np.ndarray, thresholds: Iterable[float]) -> pd.DataFrame:
    rows: List[Dict] = []
    for thr in thresholds:
        pred = (scores >= thr).astype(int)
        rows.append(
            {
                "threshold": float(thr),
                "precision": float(precision_score(y_true_binary, pred, zero_division=0)),
                "recall": float(recall_score(y_true_binary, pred, zero_division=0)),
                "f1": float(f1_score(y_true_binary, pred, zero_division=0)),
                "predicted_positive": int(pred.sum()),
            }
        )
    return pd.DataFrame(rows).sort_values("threshold").reset_index(drop=True)

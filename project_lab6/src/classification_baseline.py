from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.pipeline import Pipeline


@dataclass(frozen=True)
class BaselineConfig:
    name: str
    ngram_range: Tuple[int, int] = (1, 1)
    class_weight: Optional[str] = None
    C: float = 1.0
    max_iter: int = 500
    random_state: int = 42


def load_split_ids(path: str | Path) -> List[int]:
    p = Path(path)
    return [int(x.strip()) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


def subset_by_ids(df: pd.DataFrame, ids: List[int], id_col: str = "text_id") -> pd.DataFrame:
    id_set = set(ids)
    return df[df[id_col].astype(int).isin(id_set)].copy()


def build_pipeline(cfg: BaselineConfig) -> Pipeline:
    return Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    analyzer="word",
                    ngram_range=cfg.ngram_range,
                    sublinear_tf=True,
                    min_df=2,
                ),
            ),
            (
                "clf",
                LogisticRegression(
                    max_iter=cfg.max_iter,
                    class_weight=cfg.class_weight,
                    C=cfg.C,
                    random_state=cfg.random_state,
                ),
            ),
        ]
    )


def evaluate_baseline(
    cfg: BaselineConfig,
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    test_df: pd.DataFrame,
    text_col: str = "text",
    label_col: str = "label",
) -> Dict:
    pipe = build_pipeline(cfg)

    X_train = train_df[text_col].astype(str)
    y_train = train_df[label_col].astype(str)

    X_val = val_df[text_col].astype(str)
    y_val = val_df[label_col].astype(str)

    X_test = test_df[text_col].astype(str)
    y_test = test_df[label_col].astype(str)

    pipe.fit(X_train, y_train)

    pred_val = pipe.predict(X_val)
    pred_test = pipe.predict(X_test)

    result = {
        "name": cfg.name,
        "config": cfg,
        "pipeline": pipe,
        "val_accuracy": float(accuracy_score(y_val, pred_val)),
        "val_macro_f1": float(f1_score(y_val, pred_val, average="macro")),
        "test_accuracy": float(accuracy_score(y_test, pred_test)),
        "test_macro_f1": float(f1_score(y_test, pred_test, average="macro")),
        "val_report": classification_report(y_val, pred_val, digits=4),
        "test_report": classification_report(y_test, pred_test, digits=4),
        "y_val": y_val,
        "pred_val": pred_val,
        "y_test": y_test,
        "pred_test": pred_test,
    }
    return result


def confusion_table(y_true, y_pred, labels: List[str]) -> pd.DataFrame:
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    return pd.DataFrame(cm, index=[f"gold::{x}" for x in labels], columns=[f"pred::{x}" for x in labels])


def top_features_per_class(pipe: Pipeline, top_n: int = 10) -> Dict[str, Dict[str, List[Tuple[str, float]]]]:
    vec = pipe.named_steps["tfidf"]
    clf = pipe.named_steps["clf"]

    feat_names = vec.get_feature_names_out()
    classes = list(clf.classes_)
    coefs = clf.coef_

    out: Dict[str, Dict[str, List[Tuple[str, float]]]] = {}

    # Binary case in sklearn stores one coefficient row; map both classes for clarity.
    if len(classes) == 2 and coefs.shape[0] == 1:
        row = coefs[0]
        top_pos_idx = row.argsort()[-top_n:][::-1]
        top_neg_idx = row.argsort()[:top_n]

        out[classes[1]] = {
            "top_positive": [(feat_names[i], float(row[i])) for i in top_pos_idx],
            "top_negative": [(feat_names[i], float(row[i])) for i in top_neg_idx],
        }
        out[classes[0]] = {
            "top_positive": [(feat_names[i], float(-row[i])) for i in top_neg_idx[::-1]],
            "top_negative": [(feat_names[i], float(-row[i])) for i in top_pos_idx[::-1]],
        }
        return out

    for idx, cls in enumerate(classes):
        row = coefs[idx]
        top_pos_idx = row.argsort()[-top_n:][::-1]
        top_neg_idx = row.argsort()[:top_n]
        out[cls] = {
            "top_positive": [(feat_names[i], float(row[i])) for i in top_pos_idx],
            "top_negative": [(feat_names[i], float(row[i])) for i in top_neg_idx],
        }

    return out

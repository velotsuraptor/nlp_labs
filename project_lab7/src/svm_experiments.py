from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.svm import LinearSVC

from .baseline_cls import evaluate_pipeline


@dataclass(frozen=True)
class SVMConfig:
    name: str
    use_word: bool = True
    use_char: bool = False
    word_ngram_range: Tuple[int, int] = (1, 2)
    char_ngram_range: Tuple[int, int] = (3, 5)
    char_analyzer: str = "char_wb"
    class_weight: Optional[str] = None
    C: float = 1.0
    random_state: int = 42


def build_linear_svc_pipeline(cfg: SVMConfig) -> Pipeline:
    features = []
    if cfg.use_word:
        features.append(
            (
                "word_tfidf",
                TfidfVectorizer(
                    analyzer="word",
                    ngram_range=cfg.word_ngram_range,
                    sublinear_tf=True,
                    min_df=2,
                ),
            )
        )
    if cfg.use_char:
        features.append(
            (
                "char_tfidf",
                TfidfVectorizer(
                    analyzer=cfg.char_analyzer,
                    ngram_range=cfg.char_ngram_range,
                    sublinear_tf=True,
                    min_df=2,
                ),
            )
        )

    if not features:
        raise ValueError("At least one feature family must be enabled")

    union = features[0][1] if len(features) == 1 else FeatureUnion(features)
    return Pipeline(
        steps=[
            ("features", union),
            (
                "clf",
                LinearSVC(
                    C=cfg.C,
                    class_weight=cfg.class_weight,
                    random_state=cfg.random_state,
                ),
            ),
        ]
    )


def run_linear_svc(
    cfg: SVMConfig,
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    test_df: pd.DataFrame,
    text_col: str = "text",
    label_col: str = "label",
) -> Dict:
    pipe = build_linear_svc_pipeline(cfg)
    result = evaluate_pipeline(cfg.name, pipe, train_df, val_df, test_df, text_col=text_col, label_col=label_col)
    result["svm_config"] = cfg
    return result


def top_features_from_svm_pipeline(pipe: Pipeline, top_n: int = 10) -> Dict[str, Dict[str, List[Tuple[str, float]]]]:
    features_step = pipe.named_steps["features"]
    clf = pipe.named_steps["clf"]

    if hasattr(features_step, "get_feature_names_out"):
        feat_names = features_step.get_feature_names_out()
    else:
        raise ValueError("Feature extractor does not expose feature names")

    classes = list(clf.classes_)
    coefs = clf.coef_
    out: Dict[str, Dict[str, List[Tuple[str, float]]]] = {}

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

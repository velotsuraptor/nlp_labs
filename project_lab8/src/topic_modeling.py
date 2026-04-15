from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import numpy as np
import pandas as pd
from sklearn.decomposition import LatentDirichletAllocation, TruncatedSVD
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer


@dataclass(frozen=True)
class TopicModelConfig:
    name: str
    model_type: str
    n_topics: int
    vectorizer_type: str
    ngram_range: tuple[int, int] = (1, 1)
    min_df: int = 5
    max_df: float = 0.8
    random_state: int = 42
    max_iter: int = 30


@dataclass
class TopicModelResult:
    config: TopicModelConfig
    vectorizer: TfidfVectorizer | CountVectorizer
    model: TruncatedSVD | LatentDirichletAllocation
    doc_topic: np.ndarray
    feature_names: np.ndarray
    components: np.ndarray


def build_vectorizer(cfg: TopicModelConfig):
    kwargs = dict(
        analyzer="word",
        ngram_range=cfg.ngram_range,
        min_df=cfg.min_df,
        max_df=cfg.max_df,
    )
    if cfg.vectorizer_type == "tfidf":
        return TfidfVectorizer(sublinear_tf=True, **kwargs)
    if cfg.vectorizer_type == "count":
        return CountVectorizer(**kwargs)
    raise ValueError(f"Unsupported vectorizer_type: {cfg.vectorizer_type}")


def build_model(cfg: TopicModelConfig):
    if cfg.model_type == "lsa":
        return TruncatedSVD(n_components=cfg.n_topics, random_state=cfg.random_state)
    if cfg.model_type == "lda":
        return LatentDirichletAllocation(
            n_components=cfg.n_topics,
            random_state=cfg.random_state,
            learning_method="batch",
            max_iter=cfg.max_iter,
        )
    raise ValueError(f"Unsupported model_type: {cfg.model_type}")


def fit_topic_model(texts: pd.Series, cfg: TopicModelConfig) -> TopicModelResult:
    vec = build_vectorizer(cfg)
    X = vec.fit_transform(texts.astype(str))
    model = build_model(cfg)
    doc_topic = model.fit_transform(X)
    feature_names = vec.get_feature_names_out()
    return TopicModelResult(
        config=cfg,
        vectorizer=vec,
        model=model,
        doc_topic=doc_topic,
        feature_names=feature_names,
        components=model.components_,
    )


def topic_words(result: TopicModelResult, top_n: int = 10) -> Dict[int, List[str]]:
    out: Dict[int, List[str]] = {}
    for topic_id, row in enumerate(result.components):
        idx = row.argsort()[-top_n:][::-1]
        out[topic_id] = [str(result.feature_names[i]) for i in idx]
    return out


def topic_words_frame(result: TopicModelResult, top_n: int = 10) -> pd.DataFrame:
    rows = []
    for topic_id, words in topic_words(result, top_n=top_n).items():
        rows.append({
            "model": result.config.name,
            "topic_id": topic_id,
            "top_words": ", ".join(words),
        })
    return pd.DataFrame(rows)


def top_documents_frame(
    result: TopicModelResult,
    corpus_df: pd.DataFrame,
    text_col: str = "text",
    id_col: str = "text_id",
    label_col: str = "label",
    top_n: int = 2,
    excerpt_chars: int = 220,
) -> pd.DataFrame:
    rows = []
    for topic_id in range(result.config.n_topics):
        scores = result.doc_topic[:, topic_id]
        top_idx = np.argsort(scores)[-top_n:][::-1]
        for rank, doc_idx in enumerate(top_idx, start=1):
            row = corpus_df.iloc[int(doc_idx)]
            excerpt = str(row[text_col]).replace("\n", " ")[:excerpt_chars]
            rows.append({
                "model": result.config.name,
                "topic_id": topic_id,
                "rank": rank,
                "text_id": int(row[id_col]),
                "label": str(row[label_col]),
                "topic_score": float(scores[doc_idx]),
                "excerpt": excerpt,
            })
    return pd.DataFrame(rows)


def topic_overlap_pairs(result: TopicModelResult, top_n: int = 10, jaccard_threshold: float = 0.5) -> list[tuple[int, int, float]]:
    words = topic_words(result, top_n=top_n)
    pairs = []
    for i in range(result.config.n_topics):
        for j in range(i + 1, result.config.n_topics):
            a, b = set(words[i]), set(words[j])
            score = len(a & b) / max(1, len(a | b))
            if score >= jaccard_threshold:
                pairs.append((i, j, score))
    return pairs

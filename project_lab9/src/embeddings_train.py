from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from gensim.models import FastText, Word2Vec

RE_WS = re.compile(r"\s+")
RE_TOKEN = re.compile(r"[\w]+(?:[-'][\w]+)*", flags=re.UNICODE)


@dataclass(frozen=True)
class EmbeddingConfig:
    vector_size: int = 100
    window: int = 5
    min_count: int = 3
    sg: int = 1
    epochs: int = 20
    seed: int = 42
    workers: int = 1


def resolve_processed_data_path(project_root: Path) -> Path:
    candidates = [
        project_root / "data" / "processed_v2" / "processed_v2.csv",
        project_root.parent / "project_lab2" / "data" / "processed_v2" / "processed_v2.csv",
    ]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError("processed_v2.csv not found in project_lab9/data or project_lab2/data")


def load_embedding_corpus(project_root: Path) -> pd.DataFrame:
    path = resolve_processed_data_path(project_root)
    return pd.read_csv(path)


def tokenize_for_embeddings(text: str) -> list[str]:
    s = "" if text is None else str(text).lower()
    s = s.replace("’", "'").replace("`", "'").replace("ʼ", "'")
    s = RE_WS.sub(" ", s).strip()
    tokens = []
    for token in RE_TOKEN.findall(s):
        clean = token.strip("-'_")
        if not clean:
            continue
        if clean.isdigit():
            continue
        tokens.append(clean)
    return tokens


def prepare_sentences(df: pd.DataFrame, text_col: str = "text") -> list[list[str]]:
    sentences: list[list[str]] = []
    for text in df[text_col].astype(str):
        toks = tokenize_for_embeddings(text)
        if toks:
            sentences.append(toks)
    return sentences


def train_word2vec(sentences: list[list[str]], cfg: EmbeddingConfig) -> Word2Vec:
    return Word2Vec(
        sentences=sentences,
        vector_size=cfg.vector_size,
        window=cfg.window,
        min_count=cfg.min_count,
        sg=cfg.sg,
        epochs=cfg.epochs,
        seed=cfg.seed,
        workers=cfg.workers,
    )


def train_fasttext(sentences: list[list[str]], cfg: EmbeddingConfig) -> FastText:
    return FastText(
        sentences=sentences,
        vector_size=cfg.vector_size,
        window=cfg.window,
        min_count=cfg.min_count,
        sg=cfg.sg,
        epochs=cfg.epochs,
        seed=cfg.seed,
        workers=cfg.workers,
    )

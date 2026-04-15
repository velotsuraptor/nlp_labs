from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

import pandas as pd

BASIC_STOPWORDS = {
    "і", "й", "та", "а", "але", "або", "що", "це", "цей", "ця", "ці", "цю", "те", "той", "ті",
    "як", "же", "би", "б", "у", "в", "на", "до", "за", "з", "із", "зі", "по", "про", "для",
    "не", "ні", "так", "то", "дуже", "ще", "вже", "було", "була", "був", "бути", "є", "його",
    "її", "їх", "їм", "мене", "мені", "ми", "ви", "вони", "він", "вона", "воно", "тут", "там",
    "де", "коли", "який", "яка", "які", "яке", "яких", "якому", "якою", "свої", "свій", "свою",
    "своє", "тому", "теж", "лише", "просто", "також", "після", "перед", "під", "над", "без", "від",
    "чи", "бо", "ну", "от", "ось", "якщо", "цею", "цієї", "цього", "цьому", "більш", "менш", "були",
    "раз", "року", "весь", "всіх", "всі", "все", "йде", "були", "буде", "були", "вам", "вас", "них",
    "нас", "йти", "мав", "має", "мати", "хто", "куди", "сюди", "туди", "поки", "один", "одна", "одне",
}

DOMAIN_STOPWORDS = {
    "будь", "ласка", "будьласка", "дякую", "можна", "доброго", "день", "дня", "добрий", "добре",
    "прошу", "підкажіть", "уточніть", "допоможіть", "допомога", "питання", "щодо", "рекомендую",
    "швидко", "чітко", "зрозуміло", "люди", "людина", "будь-ласка", "думаю", "треба", "потрібно",
    "нічого", "тільки", "сказати", "казати", "разом", "слава", "україні", "добрийдень", "доброгодня",
}

DEFAULT_DROP_PATTERNS = [
    r"будь\s+ласка",
    r"добр(?:ий|ого)\s+д(?:ень|ня)",
    r"прошу\s+про\s+допомогу",
]

RE_NON_LETTERS = re.compile(r"[^\w\sіїєґІЇЄҐ-]", flags=re.UNICODE)
RE_DIGITS = re.compile(r"\d+")
RE_WS = re.compile(r"\s+")


def default_stopwords(extra_stopwords: Iterable[str] | None = None) -> set[str]:
    words = set(BASIC_STOPWORDS) | set(DOMAIN_STOPWORDS)
    if extra_stopwords:
        words |= {str(x).strip().lower() for x in extra_stopwords if str(x).strip()}
    return words


def clean_topic_text(
    text: str,
    extra_stopwords: Iterable[str] | None = None,
    min_token_len: int = 3,
    drop_patterns: Iterable[str] | None = None,
) -> str:
    s = "" if text is None else str(text).lower()
    s = s.replace("'", " ").replace("’", " ")
    for pat in (drop_patterns or DEFAULT_DROP_PATTERNS):
        s = re.sub(pat, " ", s)
    s = RE_NON_LETTERS.sub(" ", s)
    s = RE_DIGITS.sub(" ", s)
    s = RE_WS.sub(" ", s).strip()

    stopwords = default_stopwords(extra_stopwords)
    toks = [tok for tok in s.split() if len(tok) >= min_token_len and tok not in stopwords]
    return " ".join(toks)


def prepare_topic_corpus(
    df: pd.DataFrame,
    text_col: str = "text",
    min_tokens: int = 4,
    extra_stopwords: Iterable[str] | None = None,
) -> pd.DataFrame:
    out = df.copy()
    out["topic_text"] = out[text_col].map(lambda x: clean_topic_text(x, extra_stopwords=extra_stopwords))
    out["topic_token_count"] = out["topic_text"].str.split().map(lambda xs: len(xs) if isinstance(xs, list) else 0)
    out = out[out["topic_token_count"] >= min_tokens].copy()
    return out.reset_index(drop=True)


def resolve_processed_data_path(project_root: Path) -> Path:
    candidates = [
        project_root / "data" / "processed_v2" / "processed_v2.csv",
        project_root.parent / "project_lab2" / "data" / "processed_v2" / "processed_v2.csv",
    ]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError("processed_v2.csv not found in project_lab8/data or project_lab2/data")


def load_processed_corpus(project_root: Path) -> pd.DataFrame:
    path = resolve_processed_data_path(project_root)
    return pd.read_csv(path)

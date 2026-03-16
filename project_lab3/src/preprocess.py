from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Tuple


RE_WS = re.compile(r"\s+")
RE_URL = re.compile(r"(https?://\S+|www\.\S+)", re.IGNORECASE)
RE_EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
RE_PHONE = re.compile(r"(\+?\d[\d\s\-\(\)]{7,}\d)")

APOSTROPHES = {"’": "'", "ʼ": "'", "`": "'", "´": "'"}

QUOTES = {"«": '"', "»": '"', "„": '"', "“": '"', "”": '"', "‟": '"'}
DASHES = {"–": "-", "—": "-", "−": "-", "-": "-"}

NBSP = "\u00A0"
PROT_DOT = "<DOT>"
PROT_DECIMAL = "<DECIMAL_DOT>"

UA_ABBR = [
    "м", "вул", "пл", "пр", "пров", "р", "ст", "с", "ім", "п", "т", "див", "напр",
    "тобто", "тд", "т.д", "і т.д", "і т.п", "тис", "млн", "тел"
]


@dataclass(frozen=True)
class PreprocessResult:
    clean: str
    normalized: str
    masked: str
    sentences: List[str]
    stats: Dict[str, int]


def clean_text(text: str) -> str:
    s = "" if text is None else str(text)
    s = s.replace(NBSP, " ")
    s = RE_WS.sub(" ", s).strip()
    return s


def normalize_text(text: str) -> str:
    s = "" if text is None else str(text)

    for a, b in APOSTROPHES.items():
        s = s.replace(a, b)

    for a, b in QUOTES.items():
        s = s.replace(a, b)

    for a, b in DASHES.items():
        s = s.replace(a, b)

    s = re.sub(r"(?<=[А-Яа-яІіЇїЄєҐґ])i(?=[А-Яа-яІіЇїЄєҐґ])", "і", s)
    s = re.sub(r"(?<=[А-Яа-яІіЇїЄєҐґ])I(?=[А-Яа-яІіЇїЄєҐґ])", "І", s)

    s = RE_WS.sub(" ", s).strip()
    return s


def mask_pii(text: str) -> Tuple[str, Dict[str, int]]:
    s = "" if text is None else str(text)
    stats = {"url": 0, "email": 0, "phone": 0}

    def _sub_count(pattern: re.Pattern, repl: str, key: str, s_in: str) -> str:
        matches = pattern.findall(s_in)
        stats[key] += len(matches)
        return pattern.sub(repl, s_in)

    s = _sub_count(RE_URL, "<URL>", "url", s)
    s = _sub_count(RE_EMAIL, "<EMAIL>", "email", s)
    s = _sub_count(RE_PHONE, "<PHONE>", "phone", s)

    s = RE_WS.sub(" ", s).strip()
    return s, stats


def _protect_abbreviations(text: str) -> str:
    s = text
    for ab in UA_ABBR:
        ab_esc = re.escape(ab)
        s = re.sub(rf"\b{ab_esc}\.", f"{ab}{PROT_DOT}", s, flags=re.IGNORECASE)
    return s


def _protect_decimals_and_versions(text: str) -> str:
    return re.sub(r"(?<=\d)\.(?=\d)", PROT_DECIMAL, text)


def sentence_split(text: str) -> List[str]:
    s = "" if text is None else str(text)
    s = s.strip()
    if not s:
        return []

    s = _protect_abbreviations(s)
    s = _protect_decimals_and_versions(s)

    parts = re.split(r'(?<=[.!?])\s+(?=(["\)\]]?\s*)?[A-ZА-ЯІЇЄҐ])', s)

    sentences: List[str] = []
    buf = ""
    for p in parts:
        if p is None:
            continue
        if p.strip() in ['"', ")", "]", ""]:
            continue
        if buf:
            candidate = (buf + " " + p).strip()
            buf = ""
        else:
            candidate = p.strip()
        if candidate:
            sentences.append(candidate)

    restored = []
    for sent in sentences:
        sent = sent.replace(PROT_DECIMAL, ".").replace(PROT_DOT, ".")
        sent = RE_WS.sub(" ", sent).strip()
        if sent:
            restored.append(sent)
    return restored


def preprocess(text: str) -> PreprocessResult:
    raw = "" if text is None else str(text)
    clean = clean_text(raw)
    norm = normalize_text(clean)
    masked, pii_stats = mask_pii(norm)
    sents = sentence_split(masked)

    stats = {
        "repl_url": pii_stats["url"],
        "repl_email": pii_stats["email"],
        "repl_phone": pii_stats["phone"],
        "n_sentences": len(sents),
        "len_chars_before": len(raw),
        "len_chars_after": len(masked),
    }
    return PreprocessResult(clean=clean, normalized=norm, masked=masked, sentences=sents, stats=stats)



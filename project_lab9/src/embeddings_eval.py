from __future__ import annotations

from typing import Iterable

import pandas as pd


def _is_fasttext_model(model) -> bool:
    return model.__class__.__name__ == "FastText"


def safe_neighbors(model, word: str, topn: int = 10) -> dict:
    kv = model.wv
    try:
        neighbors = kv.most_similar(word, topn=topn)
        return {
            "word": word,
            "status": "ok",
            "in_vocab": word in kv.key_to_index,
            "neighbors": [(str(token), float(score)) for token, score in neighbors],
        }
    except KeyError:
        if _is_fasttext_model(model):
            try:
                neighbors = kv.most_similar(positive=[kv[word]], topn=topn)
                return {
                    "word": word,
                    "status": "oov_subword",
                    "in_vocab": False,
                    "neighbors": [(str(token), float(score)) for token, score in neighbors],
                }
            except Exception:
                pass
        return {
            "word": word,
            "status": "oov",
            "in_vocab": False,
            "neighbors": [],
        }


def format_neighbors(result: dict) -> str:
    if not result["neighbors"]:
        return f"[{result['status']}]"
    prefix = ""
    if result["status"] == "oov_subword":
        prefix = "[oov_subword] "
    parts = [f"{token} ({score:.3f})" for token, score in result["neighbors"]]
    return prefix + ", ".join(parts)


def compare_models_for_word(word: str, w2v_model, fasttext_model, topn: int = 10) -> dict:
    w2v = safe_neighbors(w2v_model, word, topn=topn)
    fasttext = safe_neighbors(fasttext_model, word, topn=topn)
    return {
        "word": word,
        "word2vec": w2v,
        "fasttext": fasttext,
    }


def build_neighbors_table(
    words_by_type: Iterable[tuple[str, str]],
    w2v_model,
    fasttext_model,
    usefulness_map: dict[str, str] | None = None,
    comment_map: dict[str, str] | None = None,
    topn: int = 10,
) -> pd.DataFrame:
    rows = []
    usefulness_map = usefulness_map or {}
    comment_map = comment_map or {}
    for word, word_type in words_by_type:
        cmp = compare_models_for_word(word, w2v_model, fasttext_model, topn=topn)
        rows.append(
            {
                "Word": word,
                "Type": word_type,
                "Word2Vec neighbors": format_neighbors(cmp["word2vec"]),
                "FastText neighbors": format_neighbors(cmp["fasttext"]),
                "Useful?": usefulness_map.get(word, ""),
                "Comment": comment_map.get(word, ""),
            }
        )
    return pd.DataFrame(rows)


def build_domain_terms_table(
    terms: list[str],
    w2v_model,
    fasttext_model,
    judgement_map: dict[str, str],
    topn: int = 10,
) -> pd.DataFrame:
    rows = []
    for term in terms:
        cmp = compare_models_for_word(term, w2v_model, fasttext_model, topn=topn)
        rows.append(
            {
                "term": term,
                "word2vec_neighbors": format_neighbors(cmp["word2vec"]),
                "fasttext_neighbors": format_neighbors(cmp["fasttext"]),
                "judgement": judgement_map.get(term, ""),
            }
        )
    return pd.DataFrame(rows)


def build_case_summary(
    case_words: list[str],
    label_map: dict[str, str],
    rationale_map: dict[str, str],
    w2v_model,
    fasttext_model,
    topn: int = 10,
) -> pd.DataFrame:
    rows = []
    for word in case_words:
        cmp = compare_models_for_word(word, w2v_model, fasttext_model, topn=topn)
        rows.append(
            {
                "word": word,
                "label": label_map[word],
                "word2vec_neighbors": format_neighbors(cmp["word2vec"]),
                "fasttext_neighbors": format_neighbors(cmp["fasttext"]),
                "rationale": rationale_map[word],
            }
        )
    return pd.DataFrame(rows)

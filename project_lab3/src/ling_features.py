from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Tuple

import stanza

RE_WS = re.compile(r"\s+")

@dataclass(frozen=True)
class LingResult:
    lemma_text: str
    upos_seq: str
    tokens: List[str]
    lemmas: List[str]
    upos: List[str]

def build_stanza_pipeline() -> stanza.Pipeline:
    stanza.download("uk", processors="tokenize,pos,lemma", verbose=False)
    nlp = stanza.Pipeline(
        lang="uk",
        processors="tokenize,pos,lemma",
        tokenize_no_ssplit=True,
        verbose=False,
        use_gpu=False
    )
    return nlp

def _flatten_doc(doc) -> Tuple[List[str], List[str], List[str]]:
    tokens, lemmas, upos = [], [], []
    for sent in doc.sentences:
        for w in sent.words:
            tokens.append(w.text)
            lemmas.append(w.lemma if w.lemma else w.text)
            upos.append(w.upos if w.upos else "X")
    return tokens, lemmas, upos

def add_ling_features(text: str, nlp: stanza.Pipeline) -> LingResult:
    s = "" if text is None else str(text)
    s = RE_WS.sub(" ", s).strip()
    if not s:
        return LingResult(lemma_text="", upos_seq="", tokens=[], lemmas=[], upos=[])

    doc = nlp(s)
    tokens, lemmas, upos = _flatten_doc(doc)

    return LingResult(
        lemma_text=" ".join(lemmas),
        upos_seq=" ".join(upos),
        tokens=tokens,
        lemmas=lemmas,
        upos=upos,
    )

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json

import pandas as pd
import stanza


@dataclass(frozen=True)
class EntitySpan:
    text: str
    start: int
    end: int
    label: str
    source: str

    def to_dict(self) -> dict:
        return asdict(self)


def resolve_processed_data_path(project_root: Path) -> Path:
    candidates = [
        project_root / "data" / "processed_v2" / "processed_v2.csv",
        project_root.parent / "project_lab2" / "data" / "processed_v2" / "processed_v2.csv",
    ]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError("processed_v2.csv not found in project_lab10/data or project_lab2/data")


def load_processed_corpus(project_root: Path) -> pd.DataFrame:
    return pd.read_csv(resolve_processed_data_path(project_root))


def load_eval_set(path: str | Path) -> list[dict]:
    rows = []
    with Path(path).open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def ensure_stanza_pipeline() -> stanza.Pipeline:
    stanza.download("uk", processors="tokenize,ner", verbose=False)
    return stanza.Pipeline(
        "uk",
        processors="tokenize,ner",
        tokenize_no_ssplit=True,
        verbose=False,
        use_gpu=False,
    )


def map_stanza_label(label: str) -> str:
    mapping = {
        "PERS": "PERSON",
        "ORG": "ORG",
        "LOC": "LOC",
        "MISC": "MISC",
    }
    return mapping.get(label, label)


def baseline_inference(text: str, nlp: stanza.Pipeline) -> list[EntitySpan]:
    doc = nlp("" if text is None else str(text))
    out = []
    for ent in doc.ents:
        out.append(
            EntitySpan(
                text=ent.text,
                start=int(ent.start_char),
                end=int(ent.end_char),
                label=map_stanza_label(ent.type),
                source="baseline",
            )
        )
    return out


def entities_to_frame(entities: list[EntitySpan]) -> pd.DataFrame:
    return pd.DataFrame([x.to_dict() for x in entities])

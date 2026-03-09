from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "resources"

def load_list(path: Path) -> List[str]:
    with path.open("r", encoding="utf-8") as f:
        return [x.strip() for x in f if x.strip()]

def load_json(path: Path) -> Dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

MONTHS = load_list(RES / "months_ua.txt")
CITIES = load_list(RES / "cities_ua.txt")
ID_CTX = load_json(RES / "id_context_keywords.json")["doc_keywords"]

MONTH_MAP = {
    "січня": "01",
    "лютого": "02",
    "березня": "03",
    "квітня": "04",
    "травня": "05",
    "червня": "06",
    "липня": "07",
    "серпня": "08",
    "вересня": "09",
    "жовтня": "10",
    "листопада": "11",
    "грудня": "12",
}

RE_DATE_NUM = re.compile(r"\b(\d{1,2})[./-](\d{1,2})[./-](\d{4})\b")
RE_DATE_TEXT = re.compile(
    r"\b(\d{1,2})\s+(" + "|".join(MONTHS) + r")\s*(\d{4})?\b",
    re.IGNORECASE,
)

RE_DOC_ID = re.compile(
    r"\b(?:повідомлення|заява|документ|звернення|рішення|договір|запит|лист)\s*№?\s*(\d{1,10})\b|№\s*(\d{1,10})\b",
    re.IGNORECASE,
)

def _item(field_type: str, value: str, start: int, end: int, method: str, raw_value: Optional[str] = None, **extra) -> Dict:
    out = {
        "field_type": field_type,
        "value": value,
        "start_char": start,
        "end_char": end,
        "method": method,
    }
    if raw_value is not None:
        out["raw_value"] = raw_value
    out.update(extra)
    return out

def normalize_date_numeric(day: str, month: str, year: str) -> Optional[str]:
    try:
        d = int(day)
        m = int(month)
        y = int(year)
        if not (1 <= d <= 31 and 1 <= m <= 12):
            return None
        return f"{y:04d}-{m:02d}-{d:02d}"
    except Exception:
        return None

def normalize_date_text(day: str, month_ua: str, year: Optional[str]) -> Optional[str]:
    if not year:
        return None
    try:
        d = int(day)
        y = int(year)
        mm = MONTH_MAP.get(month_ua.lower())
        if not mm or not (1 <= d <= 31):
            return None
        return f"{y:04d}-{int(mm):02d}-{d:02d}"
    except Exception:
        return None

def extract_dates(text: str) -> List[Dict]:
    text = "" if text is None else str(text)
    out: List[Dict] = []

    for m in RE_DATE_NUM.finditer(text):
        day, month, year = m.groups()
        value = normalize_date_numeric(day, month, year)
        if value is None:
            continue
        out.append(_item("DATE", value, m.start(), m.end(), "regex_date_numeric_v2", raw_value=m.group(0)))

    for m in RE_DATE_TEXT.finditer(text):
        day, month_ua, year = m.groups()
        parsed = normalize_date_text(day, month_ua, year)
        out.append(_item("DATE", parsed if parsed else m.group(0), m.start(), m.end(), "regex_date_text_v2", raw_value=m.group(0), parsed_date=parsed))

    return out

def extract_locations(text: str) -> List[Dict]:
    text = "" if text is None else str(text)
    out: List[Dict] = []

    city_forms = {
        "Київ": ["Київ", "Києві", "Києва"],
        "Львів": ["Львів", "Львові", "Львова", "Львову"],
        "Харків": ["Харків", "Харкові", "Харкова"],
        "Одеса": ["Одеса", "Одесі", "Одесу", "Одеси"],
        "Дніпро": ["Дніпро", "Дніпрі", "Дніпра"],
        "Чернівці": ["Чернівці", "Чернівцях"],
        "Суми": ["Суми", "Сумах"],
        "Полтава": ["Полтава", "Полтаві", "Полтаву"],
        "Тернопіль": ["Тернопіль", "Тернополі", "Тернополя"],
        "Івано-Франківськ": ["Івано-Франківськ", "Івано-Франківську", "Івано-Франківська"],
        "Ужгород": ["Ужгород", "Ужгороді", "Ужгорода"],
        "Запоріжжя": ["Запоріжжя", "Запоріжжі"],
        "Миколаїв": ["Миколаїв", "Миколаєві", "Миколаєва"],
        "Херсон": ["Херсон", "Херсоні", "Херсона"],
        "Черкаси": ["Черкаси", "Черкасах"],
        "Житомир": ["Житомир", "Житомирі", "Житомира"],
        "Рівне": ["Рівне", "Рівному"],
        "Луцьк": ["Луцьк", "Луцьку", "Луцька"],
        "Хмельницький": ["Хмельницький", "Хмельницькому", "Хмельницького"],
        "Вінниця": ["Вінниця", "Вінниці", "Вінницю"],
        "Чернігів": ["Чернігів", "Чернігові", "Чернігова"],
        "Кропивницький": ["Кропивницький", "Кропивницькому", "Кропивницького"],
    }

    seen = set()
    for city, forms in city_forms.items():
        for form in forms:
            pattern = re.compile(rf"\b{re.escape(form)}\b")
            for m in pattern.finditer(text):
                key = (city, m.start(), m.end())
                if key in seen:
                    continue
                seen.add(key)
                out.append(_item("LOCATION", city, m.start(), m.end(), "dict_city_ua_forms_v2", raw_value=m.group(0)))

    return out

def extract_doc_ids(text: str) -> List[Dict]:
    text = "" if text is None else str(text)
    out: List[Dict] = []

    for m in RE_DOC_ID.finditer(text):
        value = m.group(1) or m.group(2)
        if not value:
            continue

        raw = m.group(0)
        if len(value) == 4 and value.startswith("20") and raw.strip().lower().replace(" ", "") == f"№{value}".lower():
            continue

        out.append(_item("DOC_ID", value, m.start(), m.end(), "regex_doc_id_v2", raw_value=raw, id_type="DOC_ID"))

    return out

def extract_all(text: str) -> Dict[str, List[Dict]]:
    return {
        "DATE": extract_dates(text),
        "LOCATION": extract_locations(text),
        "DOC_ID": extract_doc_ids(text),
    }

from __future__ import annotations

from dataclasses import dataclass
import re

from .ner_pipeline import EntitySpan

RE_DATE_NUMERIC = re.compile(r"(?<!\d)(\d{1,2}\.\d{1,2}\.\d{4})(?=(?:\s*р(?:оку|\.)?)?\b)", flags=re.UNICODE)
RE_DATE_TEXTUAL = re.compile(
    r"(?<!\d)(\d{1,2}(?:-\d{1,2})?\s+(?:січня|лютого|березня|квітня|травня|червня|липня|серпня|вересня|жовтня|листопада|грудня))\b",
    flags=re.IGNORECASE | re.UNICODE,
)
RE_MONEY = re.compile(
    r"(?<!\d)(\d[\d\s]*\s*грн|\d+грн|\d{1,3}(?:\s\d{3})+|\d+(?:-\d+))(?!\d)",
    flags=re.IGNORECASE | re.UNICODE,
)


@dataclass(frozen=True)
class PhraseRule:
    phrase: str
    label: str


PHRASE_RULES = [
    PhraseRule("єВідновлення", "DOMAIN"),
    PhraseRule("євідновлення", "DOMAIN"),
    PhraseRule("Дія", "DOMAIN"),
    PhraseRule("дії", "DOMAIN"),
    PhraseRule("ЦНАП", "ORG"),
    PhraseRule("ЦНАПі", "ORG"),
    PhraseRule("КНТЕУ", "ORG"),
    PhraseRule("Ратуша", "LOC"),
    PhraseRule("податкова основянського району", "ORG"),
    PhraseRule("Повідомлення про пошкоджене майно", "DOMAIN"),
]


def _match_to_entity(match: re.Match, label: str, text: str, source: str) -> EntitySpan:
    start = match.start(1) if match.lastindex else match.start()
    end = match.end(1) if match.lastindex else match.end()
    return EntitySpan(
        text=text[start:end],
        start=int(start),
        end=int(end),
        label=label,
        source=source,
    )


def date_rule_entities(text: str) -> list[EntitySpan]:
    out = []
    for rx in (RE_DATE_NUMERIC, RE_DATE_TEXTUAL):
        for match in rx.finditer(text):
            out.append(_match_to_entity(match, "DATE", text, "rule_date"))
    return out


def money_rule_entities(text: str) -> list[EntitySpan]:
    out = []
    for match in RE_MONEY.finditer(text):
        value = text[match.start() : match.end()]
        if "грн" not in value and len(value.strip()) < 5:
            continue
        out.append(_match_to_entity(match, "MONEY", text, "rule_money"))
    return out


def phrase_rule_entities(text: str) -> list[EntitySpan]:
    out = []
    for rule in PHRASE_RULES:
        pattern = re.compile(rf"(?<!\w){re.escape(rule.phrase)}(?!\w)", flags=re.IGNORECASE | re.UNICODE)
        for match in pattern.finditer(text):
            out.append(
                EntitySpan(
                    text=text[match.start() : match.end()],
                    start=match.start(),
                    end=match.end(),
                    label=rule.label,
                    source="rule_phrase",
                )
            )
    return out


def _overlap(a: EntitySpan, b: EntitySpan) -> bool:
    return max(a.start, b.start) < min(a.end, b.end)


def merge_entities(baseline_entities: list[EntitySpan], rule_entities: list[EntitySpan]) -> list[EntitySpan]:
    merged: list[EntitySpan] = []
    all_entities = list(baseline_entities)
    for rule_ent in rule_entities:
        replaced = False
        for idx, base_ent in enumerate(all_entities):
            if rule_ent.start == base_ent.start and rule_ent.end == base_ent.end and rule_ent.label == base_ent.label:
                replaced = True
                break
            if _overlap(rule_ent, base_ent):
                if rule_ent.label in {"DATE", "MONEY", "DOMAIN", "LOC", "ORG"}:
                    all_entities[idx] = rule_ent
                    replaced = True
                    break
        if not replaced:
            all_entities.append(rule_ent)
    dedup = {}
    for ent in all_entities:
        dedup[(ent.start, ent.end, ent.label, ent.text)] = ent
    merged = list(dedup.values())
    merged.sort(key=lambda x: (x.start, x.end, x.label))
    return merged


def hybrid_entities(text: str, baseline_entities: list[EntitySpan]) -> list[EntitySpan]:
    rules = []
    rules.extend(date_rule_entities(text))
    rules.extend(money_rule_entities(text))
    rules.extend(phrase_rule_entities(text))
    return merge_entities(baseline_entities, rules)

from __future__ import annotations

from collections import Counter, defaultdict

import pandas as pd

from .ner_pipeline import EntitySpan


def entity_from_expected(item: dict) -> EntitySpan:
    return EntitySpan(
        text=item["text"],
        start=int(item["start"]),
        end=int(item["end"]),
        label=item["label"],
        source="gold",
    )


def spans_overlap(a: EntitySpan, b: EntitySpan) -> bool:
    return max(a.start, b.start) < min(a.end, b.end)


def compare_entities(expected: list[EntitySpan], predicted: list[EntitySpan]) -> dict:
    exact_expected = {(e.start, e.end, e.label): e for e in expected}
    exact_pred = {(p.start, p.end, p.label): p for p in predicted}
    correct_keys = set(exact_expected).intersection(exact_pred)

    correct = [exact_expected[k] for k in correct_keys]
    missed = []
    false_positive = []
    errors = []

    for e in expected:
        key = (e.start, e.end, e.label)
        if key in correct_keys:
            continue
        overlapping = [p for p in predicted if spans_overlap(e, p)]
        if overlapping:
            same_label = [p for p in overlapping if p.label == e.label]
            if same_label:
                p = same_label[0]
                category = "boundary error"
                pred_text = p.text
            else:
                p = overlapping[0]
                category = "type error"
                pred_text = f"{p.text} [{p.label}]"
        else:
            category = "missed domain entity" if e.label == "DOMAIN" else "missed entity"
            pred_text = ""
        missed.append(e)
        errors.append(
            {
                "expected_entity": e.text,
                "expected_type": e.label,
                "predicted_entity": pred_text,
                "predicted_type": p.label if overlapping else "",
                "category": category,
            }
        )

    for p in predicted:
        key = (p.start, p.end, p.label)
        if key in correct_keys:
            continue
        overlapping = [e for e in expected if spans_overlap(e, p)]
        if not overlapping:
            false_positive.append(p)
            errors.append(
                {
                    "expected_entity": "",
                    "expected_type": "",
                    "predicted_entity": p.text,
                    "predicted_type": p.label,
                    "category": "false positive",
                }
            )

    return {
        "correct": correct,
        "missed": missed,
        "false_positive": false_positive,
        "errors": errors,
    }


def aggregate_entity_counts(records: list[dict], system_key: str) -> pd.DataFrame:
    counts = defaultdict(Counter)
    for record in records:
        cmp = record[system_key]
        for ent in cmp["correct"]:
            counts[ent.label]["correct"] += 1
        for ent in cmp["missed"]:
            counts[ent.label]["missed"] += 1
        for ent in cmp["false_positive"]:
            counts[ent.label]["false_positive"] += 1
    rows = []
    for label, ctr in sorted(counts.items()):
        correct = ctr["correct"]
        missed = ctr["missed"]
        fp = ctr["false_positive"]
        precision = correct / (correct + fp) if correct + fp else 0.0
        recall = correct / (correct + missed) if correct + missed else 0.0
        rows.append(
            {
                "label": label,
                "correct": correct,
                "missed": missed,
                "false_positive": fp,
                "rough_precision": round(precision, 4),
                "rough_recall": round(recall, 4),
            }
        )
    return pd.DataFrame(rows)


def build_output_examples(records: list[dict], system_key: str) -> pd.DataFrame:
    rows = []
    for record in records:
        predicted = record[system_key]["predicted"]
        expected = record["expected"]
        rows.append(
            {
                "text_id": record["text_id"],
                "text": record["text"],
                "predicted_entities": [(x.text, x.label) for x in predicted],
                "expected_entities": [(x.text, x.label) for x in expected],
            }
        )
    return pd.DataFrame(rows)


def build_error_frame(records: list[dict], system_key: str) -> pd.DataFrame:
    rows = []
    for record in records:
        for err in record[system_key]["errors"]:
            rows.append(
                {
                    "text_id": record["text_id"],
                    "text_excerpt": record["text"][:220],
                    "expected_entity": err["expected_entity"],
                    "expected_type": err["expected_type"],
                    "predicted_entity": err["predicted_entity"],
                    "predicted_type": err["predicted_type"],
                    "category": err["category"],
                }
            )
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    explanation_map = {
        "boundary error": "Model or rule found the right area but the span boundaries did not match the expected entity.",
        "type error": "The system found an overlapping span but assigned the wrong entity type.",
        "missed domain entity": "Baseline or hybrid missed a corpus-specific entity that likely needs domain rules.",
        "missed entity": "Expected entity was not extracted at all.",
        "false positive": "The system predicted an entity where no gold entity was expected.",
    }
    df["explanation"] = df["category"].map(explanation_map).fillna("Manual review needed.")
    return df

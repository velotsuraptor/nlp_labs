from __future__ import annotations

from typing import Any


def normalize_feats(feats: dict[str, Any] | None) -> str:
    if not feats:
        return "_"
    parts: list[str] = []
    for key in sorted(feats):
        value = feats[key]
        if isinstance(value, (list, tuple)):
            value_str = ",".join(str(item) for item in value)
        else:
            value_str = str(value)
        parts.append(f"{key}={value_str}")
    return "|".join(parts) if parts else "_"


def make_label(token: dict[str, Any], label_field: str) -> str:
    upos = token["upos"]
    if label_field == "upos":
        return upos
    if label_field == "joint":
        feats = token.get("feats_str", "_")
        return f"{upos}||{feats}"
    raise ValueError(f"Unsupported label_field={label_field}")


def split_joint_label(label: str) -> tuple[str, str]:
    if "||" not in label:
        return label, "_"
    upos, feats = label.split("||", 1)
    return upos, feats or "_"


def token_to_features(sentence_tokens: list[dict[str, Any]], index: int) -> dict[str, Any]:
    token = sentence_tokens[index]
    form = token["form"]
    lower = form.lower()

    features: dict[str, Any] = {
        "bias": 1.0,
        "form.lower": lower,
        "form.isupper": form.isupper(),
        "form.istitle": form.istitle(),
        "form.isdigit": form.isdigit(),
        "form.has_hyphen": "-" in form,
        "form.has_apostrophe": "'" in form or "’" in form or "`" in form,
        "form.is_punct": bool(form) and all(not ch.isalnum() for ch in form),
        "prefix2": lower[:2],
        "prefix3": lower[:3],
        "suffix2": lower[-2:],
        "suffix3": lower[-3:],
        "suffix4": lower[-4:],
        "position": index,
        "is_first": index == 0,
        "is_last": index == len(sentence_tokens) - 1,
    }

    if index > 0:
        prev_form = sentence_tokens[index - 1]["form"]
        prev_lower = prev_form.lower()
        features.update(
            {
                "-1:form.lower": prev_lower,
                "-1:isupper": prev_form.isupper(),
                "-1:istitle": prev_form.istitle(),
                "-1:suffix3": prev_lower[-3:],
            }
        )
    else:
        features["BOS"] = True

    if index < len(sentence_tokens) - 1:
        next_form = sentence_tokens[index + 1]["form"]
        next_lower = next_form.lower()
        features.update(
            {
                "+1:form.lower": next_lower,
                "+1:isupper": next_form.isupper(),
                "+1:istitle": next_form.istitle(),
                "+1:suffix3": next_lower[-3:],
            }
        )
    else:
        features["EOS"] = True

    return features


def sentence_to_xy(sentence: dict[str, Any], label_field: str) -> tuple[list[dict[str, Any]], list[str]]:
    tokens = sentence["tokens"]
    x_seq = [token_to_features(tokens, i) for i in range(len(tokens))]
    y_seq = [make_label(token, label_field=label_field) for token in tokens]
    return x_seq, y_seq

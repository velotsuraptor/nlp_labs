from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import jsonlines
import pandas as pd
from conllu import parse_incr

from src.features import normalize_feats


SPLITS = ("train", "dev", "test")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def token_id_is_sequence_token(token_id: Any) -> bool:
    return isinstance(token_id, int)


def parse_sentence(tokenlist: Any, split: str, sentence_index: int) -> tuple[dict[str, Any], list[dict[str, Any]], Counter]:
    metadata = getattr(tokenlist, "metadata", {}) or {}
    sentence_id = metadata.get("sent_id", f"{split}_{sentence_index:06d}")
    text = metadata.get("text", " ".join(str(token["form"]) for token in tokenlist if token_id_is_sequence_token(token["id"])))

    sentence_tokens: list[dict[str, Any]] = []
    token_rows: list[dict[str, Any]] = []
    counts = Counter()

    for token in tokenlist:
        token_id = token["id"]
        if not token_id_is_sequence_token(token_id):
            counts["skipped_non_sequence_nodes"] += 1
            continue

        feats_str = normalize_feats(token.get("feats"))
        token_record = {
            "id": token_id,
            "form": token["form"],
            "lemma": token.get("lemma") or "_",
            "upos": token.get("upos") or "X",
            "xpos": token.get("xpos") or "_",
            "feats_str": feats_str,
            "deprel": token.get("deprel") or "_",
            "head": token.get("head"),
            "misc": token.get("misc") or {},
        }
        sentence_tokens.append(token_record)
        token_rows.append(
            {
                "split": split,
                "sentence_id": sentence_id,
                "token_id": token_id,
                "form": token_record["form"],
                "lemma": token_record["lemma"],
                "upos": token_record["upos"],
                "xpos": token_record["xpos"],
                "feats": token_record["feats_str"],
            }
        )
        counts["tokens"] += 1
        counts[f"upos::{token_record['upos']}"] += 1

    sentence_record = {
        "split": split,
        "sentence_id": sentence_id,
        "text": text,
        "tokens": sentence_tokens,
    }
    counts["sentences"] += 1
    counts["max_sentence_length"] = max(counts.get("max_sentence_length", 0), len(sentence_tokens))
    return sentence_record, token_rows, counts


def load_split(conllu_path: Path, split: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]], Counter]:
    sentences: list[dict[str, Any]] = []
    token_rows: list[dict[str, Any]] = []
    split_counts = Counter()

    with conllu_path.open("r", encoding="utf-8") as handle:
        for idx, tokenlist in enumerate(parse_incr(handle), start=1):
            sentence_record, rows, counts = parse_sentence(tokenlist, split=split, sentence_index=idx)
            sentences.append(sentence_record)
            token_rows.extend(rows)
            split_counts.update(counts)

    return sentences, token_rows, split_counts


def save_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    with jsonlines.open(path, mode="w") as writer:
        writer.write_all(records)


def counter_to_dict(counter: Counter) -> dict[str, int]:
    return {key: int(value) for key, value in counter.items()}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert UD CoNLL-U files to JSONL and CSV.")
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--processed-dir", type=Path, default=Path("data/processed"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ensure_dir(args.processed_dir)

    all_token_rows: list[dict[str, Any]] = []
    dataset_stats: dict[str, Any] = {"splits": {}}

    for split in SPLITS:
        conllu_path = args.raw_dir / f"uk_iu-ud-{split}.conllu"
        if not conllu_path.exists():
            raise FileNotFoundError(
                f"Missing {conllu_path}. Run `python -m src.load_data` first or place the official file there."
            )

        sentences, token_rows, split_counts = load_split(conllu_path, split=split)
        save_jsonl(args.processed_dir / f"{split}.jsonl", sentences)
        all_token_rows.extend(token_rows)

        dataset_stats["splits"][split] = {
            "num_sentences": len(sentences),
            "num_tokens": sum(len(sentence["tokens"]) for sentence in sentences),
            "counts": counter_to_dict(split_counts),
        }
        print(f"Processed {split}: {len(sentences)} sentences, {len(token_rows)} tokens")

    tokens_df = pd.DataFrame(all_token_rows)
    tokens_df.to_csv(args.processed_dir / "tokens.csv", index=False, encoding="utf-8")

    vocab_train = set(tokens_df.loc[tokens_df["split"] == "train", "form"].str.lower())
    for split in ("dev", "test"):
        split_df = tokens_df.loc[tokens_df["split"] == split]
        oov_rate = 0.0
        if not split_df.empty:
            oov_rate = float((~split_df["form"].str.lower().isin(vocab_train)).mean())
        dataset_stats["splits"][split]["oov_rate_vs_train"] = round(oov_rate, 6)

    dataset_stats["label_inventory_upos"] = sorted(tokens_df["upos"].dropna().unique().tolist())
    dataset_stats["total_sentences"] = int(sum(item["num_sentences"] for item in dataset_stats["splits"].values()))
    dataset_stats["total_tokens"] = int(len(tokens_df))

    stats_path = args.processed_dir / "dataset_stats.json"
    stats_path.write_text(json.dumps(dataset_stats, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved tokens.csv and {stats_path}")


if __name__ == "__main__":
    main()


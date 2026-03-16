from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
from sklearn.model_selection import GroupShuffleSplit, train_test_split


@dataclass(frozen=True)
class SplitConfig:
    strategy: str = "stratified_random"
    seed: int = 42
    train_size: float = 0.8
    val_size: float = 0.1
    test_size: float = 0.1
    label_col: str = "label"
    id_col: str = "text_id"
    group_col: Optional[str] = None
    time_col: Optional[str] = None


def _validate_sizes(train_size: float, val_size: float, test_size: float) -> None:
    total = train_size + val_size + test_size
    if abs(total - 1.0) > 1e-9:
        raise ValueError(f"Split sizes must sum to 1.0, got {total}")


def _ids(df: pd.DataFrame, id_col: str) -> List[int]:
    return df[id_col].astype(int).tolist()


def _stratified_random(df: pd.DataFrame, cfg: SplitConfig) -> Dict[str, List[int]]:
    train_df, temp_df = train_test_split(
        df,
        test_size=(cfg.val_size + cfg.test_size),
        random_state=cfg.seed,
        stratify=df[cfg.label_col],
    )

    rel_val = cfg.val_size / (cfg.val_size + cfg.test_size)
    val_df, test_df = train_test_split(
        temp_df,
        test_size=(1.0 - rel_val),
        random_state=cfg.seed,
        stratify=temp_df[cfg.label_col],
    )

    return {
        "train_ids": _ids(train_df, cfg.id_col),
        "val_ids": _ids(val_df, cfg.id_col),
        "test_ids": _ids(test_df, cfg.id_col),
    }


def _group_split(df: pd.DataFrame, cfg: SplitConfig) -> Dict[str, List[int]]:
    if not cfg.group_col:
        raise ValueError("group_col is required for group strategy")

    gss = GroupShuffleSplit(n_splits=1, train_size=cfg.train_size, random_state=cfg.seed)
    train_idx, temp_idx = next(gss.split(df, groups=df[cfg.group_col]))

    train_df = df.iloc[train_idx].copy()
    temp_df = df.iloc[temp_idx].copy()

    rel_val = cfg.val_size / (cfg.val_size + cfg.test_size)
    gss2 = GroupShuffleSplit(n_splits=1, train_size=rel_val, random_state=cfg.seed)
    val_idx, test_idx = next(gss2.split(temp_df, groups=temp_df[cfg.group_col]))

    val_df = temp_df.iloc[val_idx].copy()
    test_df = temp_df.iloc[test_idx].copy()

    return {
        "train_ids": _ids(train_df, cfg.id_col),
        "val_ids": _ids(val_df, cfg.id_col),
        "test_ids": _ids(test_df, cfg.id_col),
    }


def _time_based_split(df: pd.DataFrame, cfg: SplitConfig) -> Dict[str, List[int]]:
    if not cfg.time_col:
        raise ValueError("time_col is required for time_based strategy")

    sorted_df = df.sort_values(cfg.time_col).reset_index(drop=True)
    n = len(sorted_df)

    n_train = int(round(n * cfg.train_size))
    n_val = int(round(n * cfg.val_size))
    n_test = n - n_train - n_val

    if min(n_train, n_val, n_test) <= 0:
        raise ValueError("Invalid split sizes for dataset length")

    train_df = sorted_df.iloc[:n_train]
    val_df = sorted_df.iloc[n_train : n_train + n_val]
    test_df = sorted_df.iloc[n_train + n_val :]

    return {
        "train_ids": _ids(train_df, cfg.id_col),
        "val_ids": _ids(val_df, cfg.id_col),
        "test_ids": _ids(test_df, cfg.id_col),
    }


def make_splits(
    df: pd.DataFrame,
    strategy: str = "stratified_random",
    seed: int = 42,
    train_size: float = 0.8,
    val_size: float = 0.1,
    test_size: float = 0.1,
    label_col: str = "label",
    id_col: str = "text_id",
    group_col: Optional[str] = None,
    time_col: Optional[str] = None,
) -> Dict[str, List[int]]:
    """Create deterministic train/val/test splits and return split ids."""
    _validate_sizes(train_size, val_size, test_size)

    cfg = SplitConfig(
        strategy=strategy,
        seed=seed,
        train_size=train_size,
        val_size=val_size,
        test_size=test_size,
        label_col=label_col,
        id_col=id_col,
        group_col=group_col,
        time_col=time_col,
    )

    required_cols = {cfg.id_col, cfg.label_col}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    if cfg.strategy == "stratified_random":
        return _stratified_random(df, cfg)
    if cfg.strategy == "group":
        return _group_split(df, cfg)
    if cfg.strategy == "time_based":
        return _time_based_split(df, cfg)

    raise ValueError(f"Unknown strategy: {cfg.strategy}")


def save_splits(splits: Dict[str, List[int]], out_dir: str | Path) -> Dict[str, Path]:
    """Save split id lists to txt files and return paths."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    mapping = {
        "train_ids": out / "splits_train_ids.txt",
        "val_ids": out / "splits_val_ids.txt",
        "test_ids": out / "splits_test_ids.txt",
    }

    for key, path in mapping.items():
        ids = splits.get(key, [])
        path.write_text("\n".join(str(x) for x in ids) + "\n", encoding="utf-8")

    return mapping

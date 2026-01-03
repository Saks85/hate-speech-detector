from pathlib import Path
from typing import Tuple

import pandas as pd

from .config import settings


def load_and_merge_raw() -> pd.DataFrame:
    df = pd.read_csv("data/all_data.csv")
    return df


def split_and_save(
    test_size: float = 0.1, val_size: float = 0.1, random_state: int = 42
) -> Tuple[str, str, str]:
    from sklearn.model_selection import train_test_split

    df = load_and_merge_raw()

    train_df, temp_df = train_test_split(
        df, test_size=test_size + val_size, random_state=random_state, stratify=df["label"]
    )
    relative_val_size = val_size / (test_size + val_size)
    val_df, test_df = train_test_split(
        temp_df,
        test_size=1 - relative_val_size,
        random_state=random_state,
        stratify=temp_df["label"],
    )

    processed_dir = Path(settings.DATA_PROCESSED_DIR)
    processed_dir.mkdir(parents=True, exist_ok=True)

    train_path = processed_dir / "train.csv"
    val_path = processed_dir / "val.csv"
    test_path = processed_dir / "test.csv"

    train_df.to_csv(train_path, index=False)
    val_df.to_csv(val_path, index=False)
    test_df.to_csv(test_path, index=False)

    return str(train_path), str(val_path), str(test_path)

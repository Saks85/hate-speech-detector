import sqlite3
import pandas as pd
import random
from datasets import Dataset
import datasets

LABEL_MAP = {
    "not_hate":0,
    "offensive":1,
    "hate":2,
}

def load_feedback_samples(
    db_path: str,
    limit: int = 1000,
    min_confidence: float = 0.0
):
    conn = sqlite3.connect(db_path)
    query = """
    SELECT text, correct_label, predicted_confidence
    FROM feedback
    WHERE correct_label IS NOT NULL
      AND predicted_confidence >= ?
    ORDER BY id DESC
    LIMIT ?
    """
    df = pd.read_sql(query, conn, params=(min_confidence, limit))
    conn.close()

    df["labels"] = df["correct_label"].apply(force_int_label)

    df["sample_weight"] = df["predicted_confidence"].apply(
        lambda c: 2.0 if c < 0.6 else 1.5
    )

    return df[["text", "labels", "sample_weight"]]

def force_int_label(x):
    # unwrap list like ['hate'] or [1]
    if isinstance(x, list):
        x = x[0]

    # unwrap stringified list like "['hate']"
    if isinstance(x, str):
        x = x.strip("[]'\"").lower()
        return LABEL_MAP[x]

    # already numeric
    return int(x)

def load_original_samples(original_csv, sample_size: int):
    df = pd.read_csv(original_csv)

    if "label" not in df.columns:
        raise ValueError(f"Expected 'label' column, found {df.columns}")

    if sample_size < len(df):
        df = df.sample(sample_size, random_state=42)

    # map string labels → integers
    df["labels"] = df["label"].apply(force_int_label)

    df["sample_weight"] = 1.0

    return df[["text", "labels", "sample_weight"]]


def build_replay_dataset(
    original_csv: str,
    feedback_db: str,
    original_ratio=0.7,
    total_size=3000
):
    orig_size = int(total_size * original_ratio)
    fb_size = total_size - orig_size

    orig_df = load_original_samples(original_csv, orig_size)
    fb_df = load_feedback_samples(feedback_db, fb_size)

    combined = pd.concat([orig_df, fb_df]).sample(frac=1).reset_index(drop=True)
    dataset = Dataset.from_pandas(combined)
    dataset = dataset.cast_column("labels", datasets.Value("int64"))
    return dataset

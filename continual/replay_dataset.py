import pandas as pd
import random
from datasets import Dataset
import datasets
from sqlalchemy import create_engine, text

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
    database_url = db_path
    if "://" not in database_url:
        database_url = f"sqlite:///{database_url}"

    engine = create_engine(database_url)
    query = """
    SELECT text, correct_label, predicted_confidence
    FROM feedback
    WHERE correct_label IS NOT NULL
      AND predicted_confidence >= :min_confidence
    ORDER BY id DESC
    LIMIT :limit
    """
    with engine.connect() as conn:
        df = pd.read_sql(
            text(query),
            conn,
            params={"min_confidence": min_confidence, "limit": limit},
        )

    # Keep a consistent training schema across original + feedback datasets.
    df = df.rename(columns={"text": "content"})

    df["labels"] = df["correct_label"].apply(force_int_label)

    df["sample_weight"] = df["predicted_confidence"].apply(
        lambda c: 2.0 if c < 0.6 else 1.5
    )

    return df[["content", "labels", "sample_weight"]]

def force_int_label(x):
    # unwrap list like ['hate'] or [1]
    if isinstance(x, list):
        x = x[0]

    # normalize strings
    if isinstance(x, str):
        x = x.strip("[]'\"").lower().strip()

        # normalize variants
        NORMALIZATION_MAP = {
            "normal": "not_hate",
            "not hate": "not_hate",
            "not_hate": "not_hate",

            "offensive": "offensive",

            "hate": "hate",
            "hate speech": "hate",
            "hateful": "hate",
        }

        if x not in NORMALIZATION_MAP:
            raise ValueError(f"Unknown label in feedback data: {x}")

        return LABEL_MAP[NORMALIZATION_MAP[x]]

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

    return df[["content", "labels", "sample_weight"]]


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

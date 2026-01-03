from typing import Optional

import pandas as pd
from sqlalchemy.orm import Session

from db.models import Feedback


def feedback_to_dataframe(db: Session, only_corrected: bool = True) -> pd.DataFrame:
    """
    Export feedback entries as a dataframe for additional training.
    """
    query = db.query(Feedback)
    if only_corrected:
        query = query.filter(Feedback.correct_label.isnot(None))

    rows = query.all()
    records = []
    for fb in rows:
        label = fb.correct_label or fb.predicted_label
        records.append({"text": fb.text, "label": label})
    return pd.DataFrame.from_records(records)


def append_feedback_to_training(
    train_df: pd.DataFrame, feedback_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Merge feedback examples into training dataset.
    """
    if feedback_df.empty:
        return train_df
    combined = pd.concat([train_df, feedback_df], ignore_index=True)
    combined.drop_duplicates(subset=["text"], keep="last", inplace=True)
    return combined

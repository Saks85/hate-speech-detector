import os
from dataclasses import dataclass
from typing import Dict

import numpy as np
import pandas as pd
import torch
from datasets import Dataset
from sklearn.metrics import accuracy_score, f1_score
from transformers import (
    AutoConfig,
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
)

from .config import settings
from .preprocessing import TextPreprocessor, PreprocessingConfig
from .model import INV_LABEL_MAP


@dataclass
class TrainConfig:
    model_name: str = settings.BASE_MODEL_NAME
    num_labels: int = settings.NUM_LABELS
    output_dir: str = settings.MODEL_DIR
    max_length: int = settings.MAX_LENGTH


def load_split(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def prepare_dataset(df: pd.DataFrame, preprocessor: TextPreprocessor) -> Dataset:
    texts = df["text"].tolist()
    labels = df["label"].apply(lambda x: INV_LABEL_MAP.get(x, int(x))).tolist()

    processed_texts = []
    for t in texts:
        preproc = preprocessor.preprocess(t)
        processed_texts.append(preproc["lemmatized"] or preproc["normalized"])

    dataset = Dataset.from_dict({"text": processed_texts, "label": labels})
    return dataset


def tokenize_fn(examples, tokenizer, max_length: int):
    return tokenizer(
        examples["text"],
        truncation=True,
        padding="max_length",
        max_length=max_length,
    )


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    acc = accuracy_score(labels, preds)
    f1_macro = f1_score(labels, preds, average="macro")
    f1_weighted = f1_score(labels, preds, average="weighted")
    return {
        "accuracy": acc,
        "f1_macro": f1_macro,
        "f1_weighted": f1_weighted,
    }


def train():
    train_df = load_split(settings.TRAIN_FILE)
    val_df = load_split(settings.VAL_FILE)

    preprocessor = TextPreprocessor(PreprocessingConfig())
    train_ds = prepare_dataset(train_df, preprocessor)
    val_ds = prepare_dataset(val_df, preprocessor)

    cfg = TrainConfig()

    tokenizer = AutoTokenizer.from_pretrained(cfg.model_name)
    model_config = AutoConfig.from_pretrained(
        cfg.model_name, num_labels=cfg.num_labels
    )
    model = AutoModelForSequenceClassification.from_pretrained(
        cfg.model_name, config=model_config
    )

    train_ds = train_ds.map(
        lambda batch: tokenize_fn(batch, tokenizer, cfg.max_length), batched=True
    )
    val_ds = val_ds.map(
        lambda batch: tokenize_fn(batch, tokenizer, cfg.max_length), batched=True
    )

    train_ds.set_format(type="torch", columns=["input_ids", "attention_mask", "label"])
    val_ds.set_format(type="torch", columns=["input_ids", "attention_mask", "label"])

    training_args = TrainingArguments(
        output_dir=cfg.output_dir,
        evaluation_strategy="steps",
        save_strategy="steps",
        save_total_limit=2,
        logging_steps=settings.LOGGING_STEPS,
        eval_steps=settings.LOGGING_STEPS,
        learning_rate=settings.LEARNING_RATE,
        per_device_train_batch_size=settings.TRAIN_BATCH_SIZE,
        per_device_eval_batch_size=settings.EVAL_BATCH_SIZE,
        num_train_epochs=settings.NUM_EPOCHS,
        weight_decay=settings.WEIGHT_DECAY,
        warmup_ratio=settings.WARMUP_RATIO,
        load_best_model_at_end=True,
        metric_for_best_model="f1_macro",
        greater_is_better=True,
        seed=settings.SEED,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics,
    )

    trainer.train()
    trainer.save_model(cfg.output_dir)
    tokenizer.save_pretrained(cfg.output_dir)
    print(f"Saved model to {cfg.output_dir}")


if __name__ == "__main__":
    os.makedirs(settings.MODEL_DIR, exist_ok=True)
    train()

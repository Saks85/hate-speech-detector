from transformers import (
    DistilBertForSequenceClassification,
    DistilBertTokenizerFast,
    TrainingArguments
)
from continual.replay_dataset import build_replay_dataset
from continual.weighted_trainer import FeedbackWeightedTrainer
import torch
import os
import argparse
import shutil
import tempfile
import random
import numpy as np

#MODEL_BASE = "models/transformer/v1"
#NEW_MODEL = "models/transformer/v2"

ORIGINAL_DATA = "data/processed/train.csv"
FEEDBACK_DB = "hate_speech.db"

def freeze_lower_layers(model):
    for param in model.distilbert.embeddings.parameters():
        param.requires_grad = False

    for layer in model.distilbert.transformer.layer[:3]:
        for param in layer.parameters():
            param.requires_grad = False

def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

def tokenize(batch, tokenizer):
    return tokenizer(
        batch["text"],
        truncation=True,
        padding="max_length",
        max_length=128
    )
def replace_latest_model(new_model_path: str, latest_path: str):
    tmp_dir = tempfile.mkdtemp(prefix="latest_tmp_")

    # Copy new model into temp dir first (atomic safety)
    shutil.copytree(new_model_path, tmp_dir, dirs_exist_ok=True)

    # Remove old latest
    if os.path.exists(latest_path):
        shutil.rmtree(latest_path)

    # Move temp dir → latest
    shutil.move(tmp_dir, latest_path)


def retrain(output_version: str):
    set_seed(42)
    MODEL_BASE = "models/transformer/latest"
    NEW_MODEL = f"models/transformer/{output_version}"
    tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_BASE)
    model = DistilBertForSequenceClassification.from_pretrained(
        MODEL_BASE,
        num_labels=3
    )

    freeze_lower_layers(model)

    dataset = build_replay_dataset(
        ORIGINAL_DATA,
        FEEDBACK_DB,
        original_ratio=0.7,
        total_size=3000
    )

    dataset = dataset.map(
        lambda batch: tokenize(batch, tokenizer),
        batched=True,
        remove_columns=["text"]
    )


    dataset.set_format(
        "torch",
        columns=["input_ids", "attention_mask", "labels", "sample_weight"]
    )

    args = TrainingArguments(
        output_dir="outputs/continual",
        num_train_epochs=3,
        per_device_train_batch_size=16,
        learning_rate=1e-5,
        warmup_ratio=0.1,
        lr_scheduler_type="cosine",
        logging_steps=50,
        save_strategy="no",
        report_to="none",
        seed=42
    )
    trainer = FeedbackWeightedTrainer(
        model=model,
        args=args,
        train_dataset=dataset,
        tokenizer=tokenizer
    )


    trainer.train()

    os.makedirs(NEW_MODEL, exist_ok=True)
    model.save_pretrained(NEW_MODEL)
    tokenizer.save_pretrained(NEW_MODEL)

    LATEST_MODEL = "models/transformer/latest"
    replace_latest_model(NEW_MODEL, LATEST_MODEL)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-version",
        type=str,
        required=True
    )
    args = parser.parse_args()

    retrain(output_version=args.output_version)

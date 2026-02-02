import pandas as pd
import numpy as np
from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer
from sklearn.metrics import accuracy_score, f1_score
import datasets
import torch

# =========================
# CONFIG
# =========================
TEST_CSV = "data/processed/test.csv"              # path to your test set
MODEL_V1 = "models/transformer/v20260129_231157"
MODEL_V2 = "models/transformer/v2"
MODEL_NAME = "distilbert-base-uncased"
MAX_LEN = 128

# =========================
# LOAD TEST DATA
# =========================
df = pd.read_csv(TEST_CSV)

# must match Phase-1
df["label"] = df["label"].astype(int)

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

def tokenize(batch):
    return tokenizer(
        batch["text"],
        truncation=True,
        padding="max_length",
        max_length=MAX_LEN
    )

test_ds = Dataset.from_pandas(df)
test_ds = test_ds.map(tokenize, batched=True)
test_ds = test_ds.rename_column("label", "labels")
test_ds = test_ds.cast_column("labels", datasets.Value("int64"))

test_ds.set_format(
    "torch",
    columns=["input_ids", "attention_mask", "labels"]
)

# =========================
# METRICS
# =========================
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)

    return {
        "accuracy": accuracy_score(labels, preds),
        "f1_macro": f1_score(labels, preds, average="macro"),
        "f1_weighted": f1_score(labels, preds, average="weighted")
    }

# =========================
# EVALUATION FUNCTION
# =========================
def evaluate_model(model_path):
    model = AutoModelForSequenceClassification.from_pretrained(
        model_path,
        num_labels=3
    )

    model.config.problem_type = "single_label_classification"

    trainer = Trainer(
        model=model,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics
    )

    metrics = trainer.evaluate(test_ds)
    return metrics

# =========================
# RUN EVALUATION
# =========================
print("\nEvaluating v1...")
metrics_v1 = evaluate_model(MODEL_V1)

print("\nEvaluating v2...")
metrics_v2 = evaluate_model(MODEL_V2)

# =========================
# COMPARISON
# =========================
print("\n===== MODEL COMPARISON =====")
for k in ["accuracy", "f1_macro", "f1_weighted"]:
    v1 = metrics_v1[f"eval_{k}"]
    v2 = metrics_v2[f"eval_{k}"]
    delta = v2 - v1

    print(f"{k:12} | v1: {v1:.4f} | v2: {v2:.4f} | Δ: {delta:+.4f}")

# =========================
# OPTIONAL: SAVE RESULTS
# =========================
results = pd.DataFrame([
    {"model": "v1", **{k.replace("eval_", ""): v for k, v in metrics_v1.items() if k.startswith("eval_")}},
    {"model": "v2", **{k.replace("eval_", ""): v for k, v in metrics_v2.items() if k.startswith("eval_")}},
])

results.to_csv("model_comparison.csv", index=False)
print("\nSaved results to model_comparison.csv")

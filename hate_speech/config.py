from pathlib import Path
from typing import Any, Dict

import yaml
from pydantic_settings import BaseSettings



class Settings(BaseSettings):
    PROJECT_NAME: str = "Hate Speech Detection API"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "Context-aware hate speech detector with feedback loop"
    API_PREFIX: str = "/api/v1"

    BASE_MODEL_NAME: str = "distilbert-base-uncased"
    NUM_LABELS: int = 3
    MAX_LENGTH: int = 128
    MODEL_DIR: str = "models/transformer/latest"
    SENTENCE_BERT_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"

    TRAIN_BATCH_SIZE: int = 16
    EVAL_BATCH_SIZE: int = 32
    NUM_EPOCHS: int = 3
    LEARNING_RATE: float = 5e-5
    WEIGHT_DECAY: float = 0.01
    WARMUP_RATIO: float = 0.1
    SEED: int = 42
    LOGGING_STEPS: int = 50

    DATA_RAW_DIR: str = "data/raw"
    DATA_PROCESSED_DIR: str = "data/processed"
    TRAIN_FILE: str = "data/processed/train.csv"
    VAL_FILE: str = "data/processed/val.csv"
    TEST_FILE: str = "data/processed/test.csv"

    DATABASE_URL: str = "sqlite:///./hate_speech.db"

    class Config:
        env_file = ".env"
        case_sensitive = False


def load_from_yaml(path: str = "config/config.yaml") -> Dict[str, Any]:
    config_path = Path(path)
    if not config_path.exists():
        return {}
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def get_settings() -> Settings:
    yaml_conf = load_from_yaml()
    # We could merge yaml into Settings, but to keep it simple
    # rely mostly on environment and defaults for now.
    return Settings()


settings = get_settings()

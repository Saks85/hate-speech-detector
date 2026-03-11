from fastapi import APIRouter, BackgroundTasks
from datetime import datetime
import subprocess
import os
import sys
from pathlib import Path

from api.deps import inference_service
from api.core.redis_client import clear_prediction_cache
from hate_speech.config import settings

router = APIRouter(
    prefix="/api/v1/retrain",
    tags=["Retraining"]
)

BASE_MODEL_DIR = "models/transformer"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
LATEST_MODEL_DIR = Path(settings.MODEL_DIR)
if not LATEST_MODEL_DIR.is_absolute():
    LATEST_MODEL_DIR = PROJECT_ROOT / LATEST_MODEL_DIR

BASE_MODEL_DIR = LATEST_MODEL_DIR.parent
LOCK_FILE = BASE_MODEL_DIR / ".retraining.lock"


def run_retraining(new_version: str):
    if LOCK_FILE.exists():
        return

    try:
        LOCK_FILE.touch()

        subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "retrain_from_feedback.py"),
                "--output-version",
                new_version,
            ],
            cwd=str(PROJECT_ROOT),
            check=True,
        )

        # Reload latest model after successful training
        inference_service.reload(str(LATEST_MODEL_DIR))

        # Clear prediction cache
        clear_prediction_cache()

    finally:
        if LOCK_FILE.exists():
            LOCK_FILE.unlink()


@router.post("/")
def trigger_retraining(background_tasks: BackgroundTasks):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_version = f"v{timestamp}"

    background_tasks.add_task(run_retraining, new_version)

    return {
        "status": "started",
        "new_version": new_version
    }

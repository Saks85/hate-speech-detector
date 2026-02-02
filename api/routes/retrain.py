from fastapi import APIRouter, BackgroundTasks
from datetime import datetime
import subprocess
import os
import sys

from api.deps import inference_service
from api.core.redis_client import clear_prediction_cache

router = APIRouter(
    prefix="/api/v1/retrain",
    tags=["Retraining"]
)

BASE_MODEL_DIR = "models/transformer"
LOCK_FILE = os.path.join(BASE_MODEL_DIR, ".retraining.lock")


def run_retraining(new_version: str):
    if os.path.exists(LOCK_FILE):
        return

    try:
        open(LOCK_FILE, "w").close()

        subprocess.run(
            [
                sys.executable,
                "retrain_from_feedback.py",
                "--output-version",
                new_version,
            ],
            check=True
        )

        # Reload latest model after successful training
        inference_service.reload(f"{BASE_MODEL_DIR}/latest")

        # Clear prediction cache
        clear_prediction_cache()

    finally:
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)


@router.post("/")
def trigger_retraining(background_tasks: BackgroundTasks):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_version = f"v{timestamp}"

    background_tasks.add_task(run_retraining, new_version)

    return {
        "status": "started",
        "new_version": new_version
    }

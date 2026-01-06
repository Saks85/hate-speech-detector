from fastapi import APIRouter, BackgroundTasks
from datetime import datetime
import subprocess
import os

router = APIRouter(
    prefix="/api/v1/retrain",
    tags=["Retraining"]
)

BASE_MODEL_DIR = "models/transformer"


def run_retraining(new_version: str):
    """
    Runs retraining script in background
    """
    subprocess.Popen(
        [
            "python",
            "retrain_from_feedback.py",
            "--output-version",
            new_version
        ],
        cwd=os.getcwd()
    )


@router.post("/")
def trigger_retraining(background_tasks: BackgroundTasks):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_version = f"v{timestamp}"

    background_tasks.add_task(run_retraining, new_version)

    return {
        "status": "started",
        "new_version": new_version
    }

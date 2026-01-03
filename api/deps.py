from typing import Generator

from fastapi import Depends

from db.session import SessionLocal
from hate_speech.inference import InferenceService


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Single shared inference service instance
inference_service = InferenceService()


def get_inference_service() -> InferenceService:
    return inference_service

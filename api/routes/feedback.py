from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from api.core.redis_client import set_override
from api.core.label_utils import normalize_label

from db.models import Feedback
from ..schemas import FeedbackCreate, FeedbackResponse
from ..deps import get_db

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("/", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def create_feedback(
    payload: FeedbackCreate,
    db: Session = Depends(get_db),
):
    if not payload.text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text cannot be empty.",
        )

    predicted_label = normalize_label(payload.predicted_label)
    if predicted_label is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="predicted_label must be one of: hate, offensive, not_hate",
        )

    correct_label = normalize_label(payload.correct_label) if payload.correct_label else None
    if payload.correct_label and correct_label is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="correct_label must be one of: hate, offensive, not_hate",
        )

    fb = Feedback(
        text=payload.text,
        predicted_label=predicted_label,
        predicted_confidence=payload.predicted_confidence,
        correct_label=correct_label,
        model_version=payload.model_version,
        moderator_id=payload.moderator_id,
        notes=payload.notes,
        preprocessing=payload.preprocessing,
        metadata_features=payload.metadata_features,
    )
    if fb.correct_label:
        set_override(
            text=fb.text,
            label=fb.correct_label,
            moderator=fb.moderator_id or "unknown"
        )

    db.add(fb)
    db.commit()
    db.refresh(fb)
    return fb

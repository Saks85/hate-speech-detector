from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.models import Feedback
from api.deps import get_db

router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard"])


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):

    total = db.query(Feedback).count()

    model_errors = db.query(Feedback).filter(
        Feedback.correct_label.isnot(None),
        Feedback.correct_label != Feedback.predicted_label
    ).count()

    # if you don’t yet store override flag — return 0
    overrides = 0

    return {
        "total_feedback": total,
        "model_errors": model_errors,
        "overrides": overrides
    }


@router.get("/list")
def get_list(limit: int = 200, db: Session = Depends(get_db)):

    rows = (
        db.query(Feedback)
        .order_by(Feedback.id.desc())
        .limit(limit)
        .all()
    )

    data = []

    for r in rows:
        data.append({
            "id": r.id,
            "text": r.text or "",
            "model_label": r.predicted_label or "",
            "correct_label": r.correct_label,
            "confidence": float(r.predicted_confidence) if r.predicted_confidence is not None else None,
            "timestamp": None,   # placeholder until we add timestamp
            "model_version": r.model_version or "",
        })

    return data
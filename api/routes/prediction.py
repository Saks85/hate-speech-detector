from fastapi import APIRouter, Depends, HTTPException, status
from api.core.redis_client import get_override
from api.core.label_utils import normalize_label
from hate_speech.config import settings
from hate_speech.inference import InferenceService

from ..schemas import PredictRequest, PredictResponse
from ..deps import get_inference_service

router = APIRouter(prefix="/predict", tags=["prediction"])


@router.post("/", response_model=PredictResponse)
def predict(
    request: PredictRequest,
    service: InferenceService = Depends(get_inference_service),
):  
    override = get_override(request.text)

    if override:
        override_label = normalize_label(override.get("label"))
        if override_label is None:
            override = None

    if override:
        return {
            "label": override_label,
            "confidence": 1.0,
            "probabilities": {
                "not_hate": 1.0 if override_label == "not_hate" else 0.0,
                "offensive": 1.0 if override_label == "offensive" else 0.0,
                "hate": 1.0 if override_label == "hate" else 0.0,
            },
        }

    if not request.text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text cannot be empty.",
        )

    try:
        result = service.predict(
            text=request.text,
            include_embedding=request.include_embedding,
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    response = PredictResponse(
        label=result["label"],
        confidence=result["confidence"],
        probabilities=result["probabilities"],
        preprocessing=result["preprocessing"] if request.include_metadata else None,
        metadata_features=result["metadata_features"] if request.include_metadata else None,
    )
    return response
    
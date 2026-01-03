from fastapi import APIRouter, Depends, HTTPException, status
from api.core.redis_client import get_override
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
        return {
            "label": override["label"],
            "confidence": 1.0,
            "probabilities": {
                override["label"]: 1.0
            },
            "source": "human_override"
        }

    if not request.text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text cannot be empty.",
        )

    result = service.predict(
        text=request.text,
        include_embedding=request.include_embedding,
    )

    response = PredictResponse(
        label=result["label"],
        confidence=result["confidence"],
        probabilities=result["probabilities"],
        preprocessing=result["preprocessing"] if request.include_metadata else None,
        metadata_features=result["metadata_features"] if request.include_metadata else None,
    )
    return response
    
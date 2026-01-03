from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)
    include_embedding: bool = False
    include_metadata: bool = True


class PredictResponse(BaseModel):
    label: str
    confidence: float
    probabilities: Dict[str, float]
    preprocessing: Optional[Dict[str, Any]] = None
    metadata_features: Optional[Dict[str, Any]] = None
    # embedding intentionally omitted from API response for size, but can be added


class FeedbackCreate(BaseModel):
    text: str
    predicted_label: str
    predicted_confidence: float
    correct_label: Optional[str] = None
    model_version: Optional[str] = None
    moderator_id: Optional[str] = None
    notes: Optional[str] = None
    preprocessing: Optional[Dict[str, Any]] = None
    metadata_features: Optional[Dict[str, Any]] = None


class FeedbackResponse(BaseModel):
    id: int
    text: str
    predicted_label: str
    predicted_confidence: float
    correct_label: Optional[str]
    model_version: Optional[str]
    moderator_id: Optional[str]
    notes: Optional[str]

    class Config:
        orm_mode = True

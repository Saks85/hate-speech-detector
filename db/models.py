from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.sqlite import JSON

from .base import Base


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    predicted_label = Column(String(50), nullable=False)
    predicted_confidence = Column(Float, nullable=False)
    correct_label = Column(String(50), nullable=True)
    model_version = Column(String(50), nullable=True)
    moderator_id = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)

    # optional metadata and features
    metadata_features = Column(JSON, nullable=True)
    preprocessing = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

from typing import Dict

from .config import settings
from .model import HateSpeechModel


class InferenceService:
    def __init__(self, model_dir: str = None):
        model_path = model_dir or settings.MODEL_DIR
        self.model = HateSpeechModel(model_path)

    def predict(self, text: str, include_embedding: bool = False) -> Dict:
        result = self.model.predict(text)
        if not include_embedding:
            result.pop("sentence_bert_embedding", None)
        return result

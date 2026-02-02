from typing import Dict
from .config import settings
from .model import HateSpeechModel


class InferenceService:
    def __init__(self, model_dir: str = None):
        self._model = HateSpeechModel(model_dir or settings.MODEL_DIR)

    def predict(self, text: str, include_embedding: bool = False) -> Dict:
        result = self._model.predict(text)
        if not include_embedding:
            result.pop("sentence_bert_embedding", None)
        return result

    def reload(self, new_model_dir: str):
        # Atomic model swap
        self._model = HateSpeechModel(new_model_dir)

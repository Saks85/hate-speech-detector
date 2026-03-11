from typing import Dict, Optional
from .config import settings
from .model import HateSpeechModel


class InferenceService:
    def __init__(self, model_dir: str = None):
        self._model: Optional[HateSpeechModel] = None
        self._model_dir = model_dir or settings.MODEL_DIR
        self._last_error: Optional[str] = None

    def _ensure_loaded(self) -> None:
        if self._model is not None:
            return
        try:
            self._model = HateSpeechModel(self._model_dir)
            self._last_error = None
        except Exception as exc:
            self._last_error = str(exc)
            raise RuntimeError(
                "Model is not available. Set MODEL_DIR to a valid local model path or a valid Hugging Face model id."
            ) from exc

    def predict(self, text: str, include_embedding: bool = False) -> Dict:
        self._ensure_loaded()
        result = self._model.predict(text)
        if not include_embedding:
            result.pop("sentence_bert_embedding", None)
        return result

    def reload(self, new_model_dir: str):
        # Atomic model swap
        self._model_dir = new_model_dir
        self._model = HateSpeechModel(new_model_dir)
        self._last_error = None

    def readiness(self) -> Dict[str, Optional[str]]:
        if self._model is not None:
            return {"ready": True, "error": None, "model_dir": self._model_dir}

        return {"ready": False, "error": self._last_error, "model_dir": self._model_dir}

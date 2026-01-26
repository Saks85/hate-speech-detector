from typing import Dict, List, Optional

import torch
from sentence_transformers import SentenceTransformer
from transformers import (
    AutoConfig,
    AutoModelForSequenceClassification,
    AutoTokenizer,
)

from .config import settings
from .preprocessing import TextPreprocessor, PreprocessingConfig
from .features import FeatureExtractor


LABEL_MAP = {
    0: "not_hate",
    1: "offensive",
    2: "hate",
}
INV_LABEL_MAP = {v: k for k, v in LABEL_MAP.items()}


class HateSpeechModel:
    """
    Wrapper around  Sentence-BERT + feature extractor.

    The classifier it uses is the fine-tuned transformer.
    Sentence-BERT embeddings and metadata features are exposed
    for explainability and for potential future multi-modal models.
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        device: Optional[str] = None,
    ):
        self.model_name = model_path or settings.BASE_MODEL_NAME
        self.config = AutoConfig.from_pretrained(
            self.model_name, num_labels=settings.NUM_LABELS
        )
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name, config=self.config
        )

        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()

        # Sentence-BERT for contextual embeddings
        self.sentence_bert = SentenceTransformer(settings.SENTENCE_BERT_MODEL_NAME)

        # Preprocessing & features
        self.preprocessor = TextPreprocessor(PreprocessingConfig())
        self.feature_extractor = FeatureExtractor()

    def _predict_logits(self, text: str) -> torch.Tensor:
        inputs = self.tokenizer(
            text,
            truncation=True,
            padding="max_length",
            max_length=settings.MAX_LENGTH,
            return_tensors="pt",
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
        return logits.squeeze(0)

    def predict(self, text: str) -> Dict:
        # Full pipeline
        preproc = self.preprocessor.preprocess(text)
        processed_text = preproc["lemmatized"] or preproc["normalized"]

        # Metadata features
        metadata = self.feature_extractor.extract(preproc["normalized"])

        # Transformer prediction
        logits = self._predict_logits(processed_text)
        probs = torch.softmax(logits, dim=-1).cpu().numpy()
        label_idx = int(probs.argmax())
        label = LABEL_MAP[label_idx]
        confidence = float(probs[label_idx])

        # Sentence-BERT embedding
        embedding = self.sentence_bert.encode(
            [processed_text], normalize_embeddings=True
        )[0].tolist()

        return {
            "label": label,
            "label_index": label_idx,
            "confidence": confidence,
            "probabilities": {LABEL_MAP[i]: float(p) for i, p in enumerate(probs)},
            "preprocessing": preproc,
            "metadata_features": metadata,
            "sentence_bert_embedding": embedding,  # you might not want to send full vector in API response
        }

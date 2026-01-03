from dataclasses import dataclass
from typing import Dict

from textblob import TextBlob


@dataclass
class MetadataFeatures:
    polarity: float
    subjectivity: float
    length_chars: int
    length_words: int
    exclamation_count: int
    question_count: int
    uppercase_ratio: float
    mention_count: int
    hashtag_count: int


class FeatureExtractor:
    def __init__(self):
        pass

    def extract(self, text: str) -> Dict[str, float]:
        blob = TextBlob(text)
        polarity = float(blob.sentiment.polarity)
        subjectivity = float(blob.sentiment.subjectivity)

        length_chars = len(text)
        words = text.split()
        length_words = len(words)

        exclamation_count = text.count("!")
        question_count = text.count("?")
        uppercase_chars = sum(1 for c in text if c.isupper())
        alpha_chars = sum(1 for c in text if c.isalpha())
        uppercase_ratio = (uppercase_chars / alpha_chars) if alpha_chars > 0 else 0.0

        mention_count = text.count("@")
        hashtag_count = text.count("#")

        return MetadataFeatures(
            polarity=polarity,
            subjectivity=subjectivity,
            length_chars=length_chars,
            length_words=length_words,
            exclamation_count=exclamation_count,
            question_count=question_count,
            uppercase_ratio=uppercase_ratio,
            mention_count=mention_count,
            hashtag_count=hashtag_count,
        ).__dict__

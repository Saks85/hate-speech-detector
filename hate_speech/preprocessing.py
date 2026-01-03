import re
from dataclasses import dataclass
from typing import Dict, List

import emoji
import langdetect
import spacy
from nltk.corpus import stopwords

# Run once in setup:
# import nltk; nltk.download('stopwords')


def split_hashtag(tag: str) -> str:
    """
    Very simple hashtag decomposition:
    - Split on underscores
    - Split camelCase
    """
    tag = tag.lstrip("#")
    parts = re.sub("([a-z])([A-Z])", r"\1 \2", tag)
    parts = parts.replace("_", " ")
    return parts


@dataclass
class PreprocessingConfig:
    lowercase: bool = True
    remove_urls: bool = True
    normalize_user_mentions: bool = True
    normalize_numbers: bool = False
    expand_emojis: bool = True
    hashtag_decomposition: bool = True
    lemmatize: bool = True
    remove_stopwords: bool = False
    language: str = "en"


class TextPreprocessor:
    def __init__(self, config: PreprocessingConfig = PreprocessingConfig()):
        self.config = config
        self.nlp = spacy.load("en_core_web_sm", disable=["ner", "parser"])
        self.stopwords = set(stopwords.words("english"))

        # Simple slang dictionary (extend this in a JSON or YAML file if needed)
        self.slang_map: Dict[str, str] = {
            "u": "you",
            "ur": "your",
            "r": "are",
            "idk": "i do not know",
            "imo": "in my opinion",
            "wtf": "what the fuck",
            "lmao": "laughing my ass off",
            "omg": "oh my god",
        }

    def detect_language(self, text: str) -> str:
        try:
            return langdetect.detect(text)
        except langdetect.lang_detect_exception.LangDetectException:
            return "unknown"

    def normalize_text(self, text: str) -> str:
        original_text = text

        if self.config.lowercase:
            text = text.lower()

        if self.config.remove_urls:
            text = re.sub(r"http\S+|www\.\S+", " <URL> ", text)

        if self.config.normalize_user_mentions:
            text = re.sub(r"@\w+", " <USER> ", text)

        # Hashtag decomposition
        if self.config.hashtag_decomposition:
            def replace_hashtag(m):
                return " " + split_hashtag(m.group()) + " "
            text = re.sub(r"#\w+", replace_hashtag, text)

        # Emoji to text
        if self.config.expand_emojis:
            text = emoji.demojize(text, delimiters=(" ", " "))

        # Slang mapping (token-based)
        tokens = text.split()
        tokens = [self.slang_map.get(tok, tok) for tok in tokens]
        text = " ".join(tokens)

        return text.strip()

    def lemmatize_text(self, text: str) -> str:
        if not self.config.lemmatize:
            return text
        doc = self.nlp(text)
        tokens = []
        for token in doc:
            if self.config.remove_stopwords and token.text.lower() in self.stopwords:
                continue
            if token.is_space:
                continue
            tokens.append(token.lemma_)
        return " ".join(tokens)

    def preprocess(self, text: str) -> Dict[str, str]:
        """
        Returns dict with original, normalized, lemmatized, and language.
        """
        lang = self.detect_language(text)
        normalized = self.normalize_text(text)
        lemmatized = self.lemmatize_text(normalized)

        return {
            "original": text,
            "language": lang,
            "normalized": normalized,
            "lemmatized": lemmatized,
        }

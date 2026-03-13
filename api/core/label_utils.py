from typing import Optional


LABEL_ALIASES = {
    "hate": "hate",
    "hate_speech": "hate",
    "hate speech": "hate",
    "hateful": "hate",
    "offensive": "offensive",
    "offense": "offensive",
    "normal": "not_hate",
    "not_hate": "not_hate",
    "not hate": "not_hate",
    "non_hate": "not_hate",
}


def normalize_label(label: Optional[str]) -> Optional[str]:
    if label is None:
        return None

    normalized = label.strip().lower().replace("-", " ").replace("_", " ")
    normalized = " ".join(normalized.split())

    return LABEL_ALIASES.get(normalized)

"""
Language detection and basic Hindi-to-English transliteration.

Uses langdetect for identification and a keyword map for common
Hindi/Hinglish tokens (no external translation API required).
"""

from __future__ import annotations

import re

from langdetect import DetectorFactory, detect
from langdetect.lang_detect_exception import LangDetectException

from app.config import settings

# Make langdetect deterministic
DetectorFactory.seed = 42


def detect_language(text: str) -> str:
    """Return ISO 639-1 code (e.g. 'en', 'hi'). Defaults to 'en'."""
    try:
        return detect(text)
    except LangDetectException:
        return "en"


def translate_hindi_tokens(text: str) -> str:
    """Replace known Hindi/Hinglish tokens with English equivalents.

    This is a lightweight, rule-based approach that handles the most common
    mixed-language patterns without needing an external translation API.
    For production use with heavy Hindi content, swap in Google Translate
    or IndicTrans.
    """
    words = text.split()
    translated = []
    for word in words:
        normalized = word.strip(".,!?\"'").lower()
        replacement = settings.hindi_keywords.get(normalized)
        if replacement:
            translated.append(replacement)
        else:
            translated.append(word)
    return " ".join(translated)


def process_language(text: str) -> tuple[str, str, str | None]:
    """Run language detection and optional translation.

    Returns:
        (detected_lang, processed_text, translated_text_or_None)
    """
    lang = detect_language(text)

    if lang == "hi" or _has_hindi_tokens(text):
        translated = translate_hindi_tokens(text)
        return lang, translated, translated

    return lang, text, None


def _has_hindi_tokens(text: str) -> bool:
    words = set(re.findall(r"\b\w+\b", text.lower()))
    return bool(words & set(settings.hindi_keywords.keys()))

"""
Text cleaning: noise removal, emoji handling, normalization.
"""

from __future__ import annotations

import re
import unicodedata


# Regex patterns compiled once
_URL_RE = re.compile(r"https?://\S+|www\.\S+")
_HTML_RE = re.compile(r"<[^>]+>")
_MULTI_SPACE_RE = re.compile(r"\s+")
_SPECIAL_CHARS_RE = re.compile(r"[^\w\s.,!?'\"-]")
_REPEATED_PUNCT_RE = re.compile(r"([!?.]){3,}")
_REPEATED_CHARS_RE = re.compile(r"(.)\1{3,}")


def clean_text(text: str) -> str:
    """Full cleaning pipeline for a single review string."""
    text = _strip_html(text)
    text = _strip_urls(text)
    text = _handle_emojis(text)
    text = _normalize_unicode(text)
    text = _normalize_casing(text)
    text = _reduce_repeated_chars(text)
    text = _reduce_repeated_punctuation(text)
    text = _strip_special(text)
    text = _collapse_whitespace(text)
    return text.strip()


def _strip_html(text: str) -> str:
    return _HTML_RE.sub(" ", text)


def _strip_urls(text: str) -> str:
    return _URL_RE.sub(" ", text)


def _handle_emojis(text: str) -> str:
    """Convert emojis to descriptive text tokens so sentiment is preserved."""
    result: list[str] = []
    for ch in text:
        if _is_emoji(ch):
            name = unicodedata.name(ch, "").lower()
            if name:
                result.append(f" {name.replace(' ', '_')} ")
            # drop emoji if unnamed
        else:
            result.append(ch)
    return "".join(result)


def _is_emoji(ch: str) -> bool:
    cp = ord(ch)
    return (
        0x1F600 <= cp <= 0x1F64F  # emoticons
        or 0x1F300 <= cp <= 0x1F5FF  # misc symbols
        or 0x1F680 <= cp <= 0x1F6FF  # transport
        or 0x1F1E0 <= cp <= 0x1F1FF  # flags
        or 0x2600 <= cp <= 0x26FF  # misc symbols
        or 0x2700 <= cp <= 0x27BF  # dingbats
        or 0xFE00 <= cp <= 0xFE0F  # variation selectors
        or 0x1F900 <= cp <= 0x1F9FF  # supplemental
        or 0x200D == cp  # ZWJ
    )


def _normalize_unicode(text: str) -> str:
    return unicodedata.normalize("NFKD", text)


def _normalize_casing(text: str) -> str:
    return text.lower()


def _reduce_repeated_chars(text: str) -> str:
    """sooooo gooood -> soo good (cap at 2 repeats)."""
    return _REPEATED_CHARS_RE.sub(r"\1\1", text)


def _reduce_repeated_punctuation(text: str) -> str:
    """!!!!! -> !"""
    return _REPEATED_PUNCT_RE.sub(r"\1", text)


def _strip_special(text: str) -> str:
    return _SPECIAL_CHARS_RE.sub(" ", text)


def _collapse_whitespace(text: str) -> str:
    return _MULTI_SPACE_RE.sub(" ", text)

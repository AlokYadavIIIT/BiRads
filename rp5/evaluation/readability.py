from __future__ import annotations

import re

_SENT = re.compile(r"[.!?]+")
_WORD = re.compile(r"\b\w+(?:[-']\w+)*\b")
_VOWEL = re.compile(r"[aeiouy]+", re.I)


def _count_syllables(word: str) -> int:
    w = word.lower().strip(".,;:!?()[]{}\"")
    if not w:
        return 0
    groups = len(_VOWEL.findall(w))
    if w.endswith("e") and groups > 1:
        groups -= 1
    return max(1, groups)


def _fallback(text: str) -> tuple[float, float]:
    sentences = [x for x in _SENT.split(text) if x.strip()]
    words = _WORD.findall(text)
    if not sentences or not words:
        return 0.0, 0.0
    syllables = sum(_count_syllables(w) for w in words)
    words_per_sentence = len(words) / len(sentences)
    syllables_per_word = syllables / len(words)
    grade = 0.39 * words_per_sentence + 11.8 * syllables_per_word - 15.59
    ease = 206.835 - 1.015 * words_per_sentence - 84.6 * syllables_per_word
    return grade, ease


def flesch_kincaid(text: str) -> float:
    try:
        import textstat
        return float(textstat.flesch_kincaid_grade(text))
    except Exception:
        return _fallback(text)[0]


def flesch_reading_ease(text: str) -> float:
    try:
        import textstat
        return float(textstat.flesch_reading_ease(text))
    except Exception:
        return _fallback(text)[1]

"""Arabic text normalization.

Arabic writes the same word several ways: with or without diacritics, with any
of four alef forms, with ta marbuta or ha at the end. Two spellings of one word
are two different strings to a computer, which breaks matching, deduplication
and lookup. Normalization collapses those differences.

Each step is separately switchable because the right amount of normalization
depends on the task: collapsing ta marbuta helps a search index and hurts a
morphological analyser.
"""

from __future__ import annotations

import re
import unicodedata

from .mapping import ALEF_VARIANTS, ARABIC_DIACRITICS, TATWEEL, YA_VARIANTS

_DIACRITICS = re.compile(f"[{ARABIC_DIACRITICS}]")
_TATWEEL = re.compile(TATWEEL)
_ALEF = re.compile(f"[{ALEF_VARIANTS}]")
_YA = re.compile(f"[{YA_VARIANTS}]")
_WHITESPACE = re.compile(r"\s+")

#: Arabic-Indic and extended Arabic-Indic digits, in order 0-9.
_ARABIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")


def normalize(
    text: str,
    *,
    strip_diacritics: bool = True,
    strip_tatweel: bool = True,
    unify_alef: bool = True,
    unify_ya: bool = True,
    unify_ta_marbuta: bool = False,
    unify_digits: bool = True,
    collapse_whitespace: bool = True,
    collapse_repeats: bool = False,
) -> str:
    """Normalize Arabic text.

    Args:
        strip_diacritics: drop tashkeel, which is optional in writing and
            absent from most typed text.
        strip_tatweel: drop the kashida used to stretch words visually.
        unify_alef: collapse أ إ آ ٱ to ا.
        unify_ya: collapse alef maqsura ى to ي.
        unify_ta_marbuta: collapse ة to ه. Helps search, loses a grammatical
            distinction, so it is off by default.
        unify_digits: convert Arabic-Indic digits to ASCII.
        collapse_whitespace: squeeze runs of spaces and trim.
        collapse_repeats: reduce a letter repeated three or more times to two
            (``مزيااااان`` -> ``مزياان``). Useful on social text, off by
            default because it is lossy.

    Returns:
        The normalized string.

    Example:
        >>> normalize("أَحْمَد")
        'احمد'
    """
    result = unicodedata.normalize("NFC", text)

    if strip_diacritics:
        result = _DIACRITICS.sub("", result)
    if strip_tatweel:
        result = _TATWEEL.sub("", result)
    if unify_alef:
        result = _ALEF.sub("ا", result)
    if unify_ya:
        result = _YA.sub("ي", result)
    if unify_ta_marbuta:
        result = result.replace("ة", "ه")
    if unify_digits:
        result = result.translate(_ARABIC_DIGITS)
    if collapse_repeats:
        # Three or more of the same character become two, so emphatic
        # lengthening is flattened without merging genuine doubled letters.
        result = re.sub(r"(.)\1{2,}", r"\1\1", result)
    if collapse_whitespace:
        result = _WHITESPACE.sub(" ", result).strip()

    return result


def strip_arabic_diacritics(text: str) -> str:
    """Remove tashkeel only, leaving everything else untouched."""
    return _DIACRITICS.sub("", unicodedata.normalize("NFC", text))

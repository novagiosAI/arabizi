"""Arabizi to Arabic-script transliteration.

This is a deterministic, longest-match-first mapping, not a model. That choice
has consequences worth stating plainly:

* **Arabizi is ambiguous and lossy.** Short vowels are usually omitted, so
  ``ktbt`` is كتبت but the reader supplies the vowels. ``a`` can be ا or a
  fatha that was never written; ``o`` can be و or a vowel. The output is a
  reasonable reading, not the only one.
* **It is not reversible.** Transliterating back will not reproduce the input.
* Where an exact reading matters, use this as a preprocessing step to widen
  recall, not as ground truth.

What it does guarantee: the same input always gives the same output, it never
raises on unexpected characters, and non-Arabizi runs (numbers, URLs, French
words you exclude) pass through unchanged.
"""

from __future__ import annotations

import re

from .mapping import (
    DIGIT_DIGRAPHS,
    DIGIT_MAP,
    DIGRAPHS,
    EMPHATIC_CAPITALS,
    LETTER_MAP,
)
from .wordlist import WORD_SPELLINGS

#: Protected spans copied through untouched: URLs, emails, @handles, #tags.
_PROTECTED = re.compile(
    r"(https?://\S+|www\.\S+|\S+@\S+\.\S+|[@#]\w+)",
    re.IGNORECASE,
)

#: Word boundaries. Digits count as word characters because they stand for
#: letters here: "3afak" is one word, not "3" then "afak".
_WORD = re.compile(r"[A-Za-z0-9']+")


def transliterate(
    text: str,
    *,
    emphatic_capitals: bool = False,
    keep_unknown: bool = True,
) -> str:
    """Convert Arabizi to Arabic script.

    Args:
        emphatic_capitals: read capital S, D, T, Z, H as the emphatic
            consonants ص ض ط ظ ح. Some writers use this instead of digits. Off
            by default, because in Moroccan text a capital is far more often
            just the start of a sentence.
        keep_unknown: pass characters with no mapping through unchanged. Set
            to ``False`` to drop them.

    Returns:
        The text in Arabic script.

    Example:
        >>> transliterate("salam 3lik")
        'سلام عليك'
    """
    parts = _PROTECTED.split(text)
    # re.split with a capturing group alternates: text, match, text, match...
    return "".join(
        part if index % 2 else _transliterate_run(part, emphatic_capitals, keep_unknown)
        for index, part in enumerate(parts)
    )


def _transliterate_run(text: str, emphatic_capitals: bool, keep_unknown: bool) -> str:
    """Look each word up first, then fall back to the character mapping.

    The lookup is what recovers the short vowels arabizi does not write; see
    :mod:`arabizi.wordlist`.
    """
    out: list[str] = []
    cursor = 0

    for match in _WORD.finditer(text):
        spelling = WORD_SPELLINGS.get(match.group().lower())
        if spelling is None:
            continue
        out.append(
            _transliterate_chars(
                text[cursor : match.start()], emphatic_capitals, keep_unknown
            )
        )
        out.append(spelling)
        cursor = match.end()

    out.append(_transliterate_chars(text[cursor:], emphatic_capitals, keep_unknown))
    return "".join(out)


def _transliterate_chars(text: str, emphatic_capitals: bool, keep_unknown: bool) -> str:
    out: list[str] = []
    index = 0
    length = len(text)

    while index < length:
        # Longest match first, so "ch" wins over "c" and "3'" over "3".
        pair = text[index : index + 2]

        if pair in DIGIT_DIGRAPHS:
            out.append(DIGIT_DIGRAPHS[pair])
            index += 2
            continue

        lowered_pair = pair.lower()
        if lowered_pair in DIGRAPHS:
            out.append(DIGRAPHS[lowered_pair])
            index += 2
            continue

        char = text[index]

        if emphatic_capitals and char in EMPHATIC_CAPITALS:
            out.append(EMPHATIC_CAPITALS[char])
            index += 1
            continue

        if char in DIGIT_MAP:
            out.append(DIGIT_MAP[char])
            index += 1
            continue

        lowered = char.lower()
        if lowered in LETTER_MAP:
            out.append(LETTER_MAP[lowered])
            index += 1
            continue

        if keep_unknown:
            out.append(char)
        index += 1

    return "".join(out)


def transliterate_word(word: str, **kwargs: bool) -> str:
    """Transliterate a single token. Convenience wrapper."""
    return transliterate(word, **kwargs)

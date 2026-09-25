"""Word-level language detection for mixed Moroccan text.

A single Moroccan sentence routinely carries three languages:

    "salam, wach kayn chi rendez-vous dispo today?"
     Darija        Darija      French         English

Document-level language identification returns one label for that and is
useless. This module labels every token, and says so when a token is genuinely
ambiguous instead of guessing.

Evidence is applied strongest-first:

1. Arabic script                     -> ARABIC
2. digits only / punctuation only    -> NUMBER / PUNCTUATION
3. a Latin word containing 2 3 5 6 7 8 9  -> ARABIZI  (near-certain)
4. a French-only diacritic           -> FRENCH
5. present in exactly one lexicon    -> that language
6. anything else                     -> UNKNOWN

Step 6 is the honest one. *"salam"* is Darija and *"salut"* is French, but
*"normal"* is both and *"taxi"* is everyone's. Latin words with no diacritic,
no arabizi digit and no lexicon entry cannot be resolved by rules, and this
module reports UNKNOWN rather than inventing a label. If you need those
resolved, use this as features for a classifier, not as the classifier.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from enum import Enum

from .lexicon import DARIJA_WORDS, ENGLISH_WORDS, FRENCH_WORDS


class Script(str, Enum):
    """What a token was written in."""

    ARABIC = "arabic"
    ARABIZI = "arabizi"
    FRENCH = "french"
    ENGLISH = "english"
    NUMBER = "number"
    PUNCTUATION = "punctuation"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class Token:
    """One token and what it was identified as."""

    text: str
    script: Script
    start: int
    end: int
    #: Why the label was chosen, so a surprising result can be traced.
    evidence: str = ""


_TOKEN = re.compile(r"\w+(?:[-'’]\w+)*|[^\w\s]+", re.UNICODE)
_ARABIC = re.compile(r"[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿]")
_ARABIZI_DIGIT = re.compile(r"[2356789]")
_LATIN = re.compile(r"[A-Za-z]")
#: Diacritics that occur in French but not in English.
_FRENCH_DIACRITIC = re.compile(r"[àâäéèêëîïôöùûüÿçœæ]", re.IGNORECASE)


def _strip_accents(word: str) -> str:
    decomposed = unicodedata.normalize("NFD", word)
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def detect_token(token: str) -> tuple[Script, str]:
    """Classify one token. Returns the label and the evidence for it."""
    if not token or not token.strip():
        return Script.UNKNOWN, "empty"

    if _ARABIC.search(token):
        return Script.ARABIC, "arabic script"

    stripped = token.strip(".,;:!?()[]{}\"'’«»")
    if stripped.isdigit():
        return Script.NUMBER, "digits only"
    if stripped and not any(char.isalnum() for char in stripped):
        return Script.PUNCTUATION, "punctuation only"
    if not stripped:
        return Script.PUNCTUATION, "punctuation only"

    has_latin = bool(_LATIN.search(stripped))

    # A digit sitting inside a Latin word is arabizi's signature: no French or
    # English word contains one.
    if has_latin and _ARABIZI_DIGIT.search(stripped):
        return Script.ARABIZI, "arabizi digit inside a Latin word"

    if _FRENCH_DIACRITIC.search(stripped):
        return Script.FRENCH, "French diacritic"

    lowered = stripped.lower()
    folded = _strip_accents(lowered)

    matches = []
    if lowered in DARIJA_WORDS or folded in DARIJA_WORDS:
        matches.append(Script.ARABIZI)
    if lowered in FRENCH_WORDS or folded in FRENCH_WORDS:
        matches.append(Script.FRENCH)
    if lowered in ENGLISH_WORDS or folded in ENGLISH_WORDS:
        matches.append(Script.ENGLISH)

    if len(matches) == 1:
        return matches[0], "function word"
    if len(matches) > 1:
        names = ", ".join(script.value for script in matches)
        return Script.UNKNOWN, f"ambiguous: in {names} lexicons"

    if not has_latin:
        return Script.UNKNOWN, "no Latin letters"
    return Script.UNKNOWN, "Latin word, no decisive signal"


def detect(text: str) -> list[Token]:
    """Label every token in ``text``, in order.

    Example:
        >>> [(t.text, t.script.value) for t in detect("salam les amis")]
        [('salam', 'arabizi'), ('les', 'french'), ('amis', 'unknown')]
    """
    tokens: list[Token] = []
    for match in _TOKEN.finditer(text):
        script, evidence = detect_token(match.group())
        tokens.append(
            Token(match.group(), script, match.start(), match.end(), evidence)
        )
    return tokens


def script_counts(text: str) -> dict[Script, int]:
    """How many tokens of each kind ``text`` contains."""
    counts: dict[Script, int] = {}
    for token in detect(text):
        counts[token.script] = counts.get(token.script, 0) + 1
    return counts


def is_code_switched(text: str, *, minimum: int = 2) -> bool:
    """True when the text mixes at least ``minimum`` real languages.

    Punctuation, numbers and unresolved tokens do not count as languages.
    """
    languages = {
        Script.ARABIC,
        Script.ARABIZI,
        Script.FRENCH,
        Script.ENGLISH,
    }
    present = {
        script
        for script, count in script_counts(text).items()
        if script in languages and count
    }
    return len(present) >= minimum


def dominant_script(text: str) -> Script:
    """The most frequent real language in ``text``, or UNKNOWN.

    Ties are broken in favour of the language whose token appears first, so
    the result is deterministic.
    """
    tokens = [
        token
        for token in detect(text)
        if token.script
        in {Script.ARABIC, Script.ARABIZI, Script.FRENCH, Script.ENGLISH}
    ]
    if not tokens:
        return Script.UNKNOWN

    counts: dict[Script, int] = {}
    first_seen: dict[Script, int] = {}
    for index, token in enumerate(tokens):
        counts[token.script] = counts.get(token.script, 0) + 1
        first_seen.setdefault(token.script, index)

    return min(counts, key=lambda script: (-counts[script], first_seen[script]))

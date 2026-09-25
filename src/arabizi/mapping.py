"""Arabizi-to-Arabic character mappings.

Arabizi is Arabic written in Latin letters, with digits standing in for the
sounds Latin has no letter for. The digits are close to universal across the
Arab world; **the letters are not**.

Moroccan arabizi is built on French orthography, because that is the second
language its writers were schooled in:

=========  ==============  =================
sound      Moroccan        Levantine / Gulf
=========  ==============  =================
ش          ``ch``          ``sh``
و (long)   ``ou``          ``oo`` / ``u``
ق          ``9`` / ``q``   ``2`` (glottal)
=========  ==============  =================

A transliterator tuned on Levantine data therefore reads *"chkoun"* (شكون,
"who") as if the ``ch`` were English, and gets it wrong. That difference is why
this module exists.
"""

from __future__ import annotations

#: Digits standing in for Arabic letters. Widely shared across dialects.
DIGIT_MAP: dict[str, str] = {
    "2": "ء",  # hamza
    "3": "ع",  # ayn
    "5": "خ",  # kha
    "6": "ط",  # emphatic ta
    "7": "ح",  # ha
    "8": "غ",  # ghayn (also written 3' or gh)
    "9": "ق",  # qaf - in Morocco; the Levant uses 2 for the glottal stop
}

#: Digit + apostrophe forms, tried before the bare digit.
DIGIT_DIGRAPHS: dict[str, str] = {
    "3'": "غ",
    "7'": "خ",
    "9'": "ق",
    "5'": "خ",
}

#: Latin digraphs. ``ch`` and ``ou`` are the Moroccan-specific entries.
DIGRAPHS: dict[str, str] = {
    "ch": "ش",  # French convention - Moroccan
    "sh": "ش",  # English convention - accepted as a fallback
    "kh": "خ",
    "gh": "غ",
    "th": "ث",
    "dh": "ذ",
    "ou": "و",  # French convention - Moroccan
    "oo": "و",
    "ee": "ي",
    "ii": "ي",
    "aa": "ا",
    "ss": "س",
    "ll": "ل",
}

#: Single letters. Several are genuinely ambiguous; see module docstring of
#: :mod:`arabizi.transliterate` for what that means for the output.
LETTER_MAP: dict[str, str] = {
    "a": "ا",
    "b": "ب",
    "c": "ك",
    "d": "د",
    "e": "ي",
    "f": "ف",
    "g": "ڭ",  # Moroccan gaf; Egyptians would write ج
    "h": "ه",
    "i": "ي",
    "j": "ج",
    "k": "ك",
    "l": "ل",
    "m": "م",
    "n": "ن",
    "o": "و",
    "p": "پ",
    "q": "ق",
    "r": "ر",
    "s": "س",
    "t": "ت",
    "u": "و",
    "v": "ڤ",
    "w": "و",
    "x": "كس",
    "y": "ي",
    "z": "ز",
}

#: Capitals used for emphatic consonants, a convention some writers prefer over
#: digits. Off by default: in Moroccan text a capital is far more often just the
#: start of a sentence.
EMPHATIC_CAPITALS: dict[str, str] = {
    "S": "ص",
    "D": "ض",
    "T": "ط",
    "Z": "ظ",
    "H": "ح",
    "3": "ع",
}

#: Arabic letters that carry no information for matching purposes.
ARABIC_DIACRITICS = "ؐ-ًؚ-ٰٟۖ-ۜ۟-۪ۨ-ۭ"

TATWEEL = "ـ"

#: Variants collapsed by :func:`arabizi.normalize.normalize`.
ALEF_VARIANTS = "أإآٱ"
YA_VARIANTS = "ى"

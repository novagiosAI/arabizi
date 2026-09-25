from .detect import (
    Script,
    Token,
    detect,
    detect_token,
    dominant_script,
    is_code_switched,
    script_counts,
)
from .normalize import normalize, strip_arabic_diacritics
from .transliterate import transliterate, transliterate_word

__version__ = "0.1.0"

__all__ = [
    "transliterate",
    "transliterate_word",
    "normalize",
    "strip_arabic_diacritics",
    "detect",
    "detect_token",
    "script_counts",
    "is_code_switched",
    "dominant_script",
    "Script",
    "Token",
]

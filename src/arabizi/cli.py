"""Command line entry point: ``arabizi``."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence

from .detect import Script, detect, dominant_script, is_code_switched
from .normalize import normalize
from .transliterate import transliterate


def _force_utf8() -> None:
    """Windows consoles default to a legacy code page and would raise on
    Arabic output."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8")
            except (ValueError, OSError):  # pragma: no cover
                pass


def _read_input(value: str | None) -> str:
    if value is None or value == "-":
        return sys.stdin.read()
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="arabizi",
        description=(
            "Transliterate Moroccan Arabizi, normalize Arabic, "
            "and label mixed-language text word by word."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    translit = sub.add_parser(
        "translit", help="Arabizi -> Arabic script (reads stdin with '-')"
    )
    translit.add_argument("text", nargs="?", help="text, or '-' for stdin")
    translit.add_argument(
        "--emphatic-capitals",
        action="store_true",
        help="read capital S D T Z H as ص ض ط ظ ح",
    )

    norm = sub.add_parser("normalize", help="normalize Arabic text")
    norm.add_argument("text", nargs="?", help="text, or '-' for stdin")
    norm.add_argument("--ta-marbuta", action="store_true", help="also collapse ة to ه")
    norm.add_argument(
        "--collapse-repeats",
        action="store_true",
        help="reduce a letter repeated 3+ times to 2",
    )

    det = sub.add_parser("detect", help="label each token's language")
    det.add_argument("text", nargs="?", help="text, or '-' for stdin")
    det.add_argument("--json", action="store_true", help="emit JSON")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    _force_utf8()
    args = build_parser().parse_args(argv)
    text = _read_input(getattr(args, "text", None))

    if args.command == "translit":
        print(transliterate(text, emphatic_capitals=args.emphatic_capitals))
        return 0

    if args.command == "normalize":
        print(
            normalize(
                text,
                unify_ta_marbuta=args.ta_marbuta,
                collapse_repeats=args.collapse_repeats,
            )
        )
        return 0

    tokens = detect(text)
    if args.json:
        print(
            json.dumps(
                {
                    "dominant": dominant_script(text).value,
                    "code_switched": is_code_switched(text),
                    "tokens": [
                        {
                            "text": token.text,
                            "script": token.script.value,
                            "start": token.start,
                            "end": token.end,
                            "evidence": token.evidence,
                        }
                        for token in tokens
                    ],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    width = max((len(token.text) for token in tokens), default=1)
    for token in tokens:
        if token.script in (Script.PUNCTUATION, Script.NUMBER):
            continue
        print(f"  {token.text:<{width}}  {token.script.value:<12} {token.evidence}")
    print()
    print(f"  dominant: {dominant_script(text).value}")
    print(f"  code-switched: {is_code_switched(text)}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

# Changelog

All notable changes to this project are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] — 2026-09-19

First public release.

### Added

- `transliterate()` — Moroccan Arabizi to Arabic script, using **French
  orthographic conventions** (`ch` → ش, `ou` → و, `9` → ق, `g` → ڭ) rather than the
  English ones assumed by Levantine-tuned tools, with those accepted as fallbacks.
- A word lookup table (`wordlist.py`) consulted before the character mapping, which
  recovers the short vowels arabizi does not write: `salam` → سلام, not سالام.
  Handles multi-word expansions (`mabghitch` → ما بغيتش) and spelling variants.
- URLs, emails and `@handles` are protected from transliteration.
- `normalize()` — Arabic normalization with individually switchable steps:
  diacritics, tatweel, alef and ya variants, ta marbuta, Arabic-Indic digits,
  whitespace and character repeats.
- `detect()` — **word-level** language identification for mixed Darija / French /
  English / Arabic text, returning a token, a label, character offsets and the
  evidence behind the label.
- Tokens with no decisive signal are reported `UNKNOWN` with a reason rather than
  guessed at.
- `script_counts()`, `is_code_switched()` and `dominant_script()` helpers.
- `arabizi` command line tool with `translit`, `normalize` and `detect`
  subcommands, the last with `--json`.
- UTF-8 output forced on Windows consoles so Arabic does not raise
  `UnicodeEncodeError`.
- 90 tests. No runtime dependencies. Passes `mypy --strict`.
- CI across Python 3.10–3.13 with `pytest`, `ruff` and `mypy`.

[Unreleased]: https://github.com/novagiosAI/arabizi/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/novagiosAI/arabizi/releases/tag/v0.1.0

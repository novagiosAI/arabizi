# Contributing to arabizi

Thanks for taking the time to contribute. Three kinds of contribution matter most:

1. **Spelling variants.** Arabizi is not standardised. If you write a word
   differently than this package expects, that is a bug report, not a quirk.
   Open an issue with the spelling and what it should mean.
2. **Word-list entries.** Adding a frequent Darija word to `wordlist.py` with its
   settled Arabic spelling improves transliteration more than any rule change can.
3. **Other Maghreb varieties.** Algerian and Tunisian arabizi share the French
   base and differ in detail. The package is not named `darija` by accident.

## Getting set up

```bash
git clone https://github.com/novagiosAI/arabizi.git
cd arabizi
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Before opening a pull request

```bash
pytest
ruff check .
ruff format .
mypy
```

## Adding to the word list

`wordlist.py` maps an arabizi spelling to its Arabic form. Rules to follow:

- Keys are **lowercase and punctuation-free**.
- Add **every common variant** you know of as a separate key pointing at the same
  value (`wach` and `wash`, `chkoun` and `shkoun`).
- A single arabizi token may expand to several Arabic words
  (`mabghitch` → `ما بغيتش`). That is expected.
- Add a test asserting the spelling. If you are not certain of the Arabic form,
  say so in the pull request rather than guessing — a wrong entry is worse than a
  missing one, because the fallback would at least have been transparent.

## Adding to the function-word lists

`lexicon.py` drives language detection. These lists are **small and
high-precision on purpose**:

- Add **function words only** — pronouns, prepositions, particles. Content words
  cross language boundaries constantly in Moroccan speech and prove nothing.
- Before adding a word, check it is not already in another list. A word in two
  lists is evidence of nothing, and the detector correctly reports it as
  ambiguous.
- Adding content words to raise recall will lower precision. If you want that
  trade, make it in your own application, not here.

## Design principles

1. **Never guess.** A token with no decisive signal is reported `UNKNOWN` with
   its reason. A label the package cannot justify is worse than no label.
2. **Moroccan conventions are the default.** `ch` is ش, `ou` is و, `9` is ق.
   Levantine spellings are accepted as fallbacks, never as the primary reading.
3. **Deterministic and dependency-free.** Same input, same output, no model
   download, no network.
4. **Evidence is part of the output.** Every detection carries the reason it was
   made.

## Security issues

Do not open a public issue for a vulnerability. See [SECURITY.md](SECURITY.md).

## License

By contributing, you agree that your contributions are licensed under the
[Apache License 2.0](LICENSE).

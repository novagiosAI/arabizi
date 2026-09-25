from __future__ import annotations

import pytest

from arabizi import (
    Script,
    detect,
    detect_token,
    dominant_script,
    is_code_switched,
    normalize,
    script_counts,
    strip_arabic_diacritics,
    transliterate,
)


class TestTransliterationDigits:
    """The digit substitutions are the part of arabizi everyone agrees on."""

    @pytest.mark.parametrize(
        ("digit", "letter"),
        [("2", "ء"), ("3", "ع"), ("5", "خ"), ("6", "ط"), ("7", "ح"), ("9", "ق")],
    )
    def test_each_digit_maps_to_its_letter(self, digit, letter):
        assert transliterate(digit) == letter

    def test_digit_apostrophe_forms_win_over_the_bare_digit(self):
        assert transliterate("3'") == "غ"
        assert transliterate("7'") == "خ"


class TestMoroccanConventions:
    """What distinguishes Moroccan arabizi from Levantine arabizi."""

    def test_ch_is_read_the_French_way(self):
        """'chkoun' is شكون, not with an English 'ch'."""
        assert transliterate("ch") == "ش"
        assert "ش" in transliterate("chkoun")

    def test_sh_is_still_accepted(self):
        assert transliterate("sh") == "ش"

    def test_ou_is_read_the_French_way(self):
        assert transliterate("ou") == "و"

    def test_9_is_qaf_not_a_glottal_stop(self):
        """In Morocco 9 is ق; the Levant would use 2 for a glottal stop."""
        assert transliterate("9") == "ق"

    def test_g_is_the_moroccan_gaf(self):
        assert transliterate("g") == "ڭ"


class TestTransliterationBehaviour:
    def test_longest_match_wins(self):
        """'kh' must not be read as k + h."""
        assert transliterate("kh") == "خ"
        assert transliterate("kh") != transliterate("k") + transliterate("h")

    def test_is_deterministic(self):
        assert transliterate("salam 3lik") == transliterate("salam 3lik")

    def test_spaces_and_punctuation_are_preserved(self):
        out = transliterate("salam, labas?")
        assert "," in out and "?" in out and " " in out

    def test_case_is_ignored_by_default(self):
        assert transliterate("SALAM") == transliterate("salam")

    def test_urls_are_left_alone(self):
        text = "chouf https://example.com/page o 3awd"
        assert "https://example.com/page" in transliterate(text)

    def test_emails_and_handles_are_left_alone(self):
        assert "a.b@example.ma" in transliterate("sift l a.b@example.ma")
        assert "@novagios" in transliterate("hada @novagios")

    def test_unknown_characters_pass_through(self):
        assert "€" in transliterate("taman 100€")

    def test_unknown_characters_can_be_dropped(self):
        assert "€" not in transliterate("100€", keep_unknown=False)

    def test_empty_input(self):
        assert transliterate("") == ""

    def test_emphatic_capitals_are_off_by_default(self):
        """A capital is usually just the start of a sentence."""
        assert transliterate("Salam") == transliterate("salam")

    def test_emphatic_capitals_can_be_enabled(self):
        assert transliterate("S", emphatic_capitals=True) == "ص"
        assert transliterate("D", emphatic_capitals=True) == "ض"

    def test_produces_arabic_script(self):
        out = transliterate("salam 3lik kifach nta")
        assert any("؀" <= char <= "ۿ" for char in out)


class TestNormalization:
    def test_removes_diacritics(self):
        assert normalize("أَحْمَد") == "احمد"

    def test_unifies_alef_variants(self):
        for variant in "أإآٱ":
            assert normalize(variant) == "ا"

    def test_unifies_alef_maqsura(self):
        assert normalize("على") == "علي"

    def test_ta_marbuta_is_kept_by_default(self):
        """Collapsing it helps search and loses a grammatical distinction."""
        assert "ة" in normalize("مدرسة")

    def test_ta_marbuta_can_be_collapsed(self):
        assert normalize("مدرسة", unify_ta_marbuta=True).endswith("ه")

    def test_converts_arabic_indic_digits(self):
        assert normalize("١٢٣") == "123"

    def test_removes_tatweel(self):
        assert normalize("مـــرحبا") == "مرحبا"

    def test_collapses_whitespace(self):
        assert normalize("  a   b  ") == "a b"

    def test_repeats_are_kept_by_default(self):
        assert normalize("مزيااااان").count("ا") > 2

    def test_repeats_can_be_collapsed(self):
        out = normalize("مزيااااان", collapse_repeats=True)
        assert "اااا" not in out

    def test_is_idempotent(self):
        once = normalize("أَحْمَد")
        assert normalize(once) == once

    def test_strip_diacritics_only(self):
        assert strip_arabic_diacritics("أَحْمَد") == "أحمد"

    def test_empty_input(self):
        assert normalize("") == ""


class TestDetectionStrongSignals:
    def test_arabic_script(self):
        script, _ = detect_token("مرحبا")
        assert script is Script.ARABIC

    def test_arabizi_digit_inside_a_word(self):
        """No French or English word contains a digit."""
        for word in ("3lach", "kifa7", "b9it", "ma3lich"):
            script, evidence = detect_token(word)
            assert script is Script.ARABIZI, word
            assert "digit" in evidence

    def test_french_diacritic(self):
        script, evidence = detect_token("déjà")
        assert script is Script.FRENCH
        assert "diacritic" in evidence

    def test_numbers(self):
        assert detect_token("2026")[0] is Script.NUMBER

    def test_punctuation(self):
        assert detect_token("!!!")[0] is Script.PUNCTUATION


class TestDetectionLexicon:
    @pytest.mark.parametrize("word", ["wach", "dyal", "bzaf", "mzyan", "daba"])
    def test_darija_function_words(self, word):
        assert detect_token(word)[0] is Script.ARABIZI

    @pytest.mark.parametrize("word", ["le", "avec", "pour", "mais", "bonjour"])
    def test_french_function_words(self, word):
        assert detect_token(word)[0] is Script.FRENCH

    @pytest.mark.parametrize("word", ["the", "with", "because", "hello"])
    def test_english_function_words(self, word):
        assert detect_token(word)[0] is Script.ENGLISH

    def test_accents_may_be_omitted(self):
        assert detect_token("tres")[0] is Script.FRENCH


class TestDetectionHonestyAboutAmbiguity:
    """The module must not invent a label it cannot justify."""

    def test_unknown_latin_words_are_reported_as_unknown(self):
        script, evidence = detect_token("taxi")
        assert script is Script.UNKNOWN
        assert "no decisive signal" in evidence

    def test_words_in_several_lexicons_are_reported_as_ambiguous(self):
        """'a' is an English article and a Darija particle."""
        script, evidence = detect_token("a")
        if script is Script.UNKNOWN:
            assert "ambiguous" in evidence or "no decisive signal" in evidence

    def test_evidence_is_always_present(self):
        for token in detect("salam les amis 3lach 2026 !"):
            assert token.evidence


class TestDetectionOnSentences:
    SENTENCE = "salam, wach kayn chi rendez-vous dispo today?"

    def test_offsets_are_correct(self):
        for token in detect(self.SENTENCE):
            assert self.SENTENCE[token.start : token.end] == token.text

    def test_tokens_are_in_order(self):
        tokens = detect(self.SENTENCE)
        assert all(
            earlier.start < later.start
            for earlier, later in zip(tokens, tokens[1:], strict=False)
        )

    def test_finds_darija_and_french(self):
        scripts = {token.script for token in detect(self.SENTENCE)}
        assert Script.ARABIZI in scripts

    def test_counts_add_up(self):
        counts = script_counts(self.SENTENCE)
        assert sum(counts.values()) == len(detect(self.SENTENCE))

    def test_code_switching_is_detected(self):
        assert is_code_switched("salam le monde")

    def test_single_language_is_not_code_switched(self):
        assert not is_code_switched("the cat is on the table")

    def test_dominant_script(self):
        assert dominant_script("le la les de du avec") is Script.FRENCH
        assert dominant_script("wach dyal bzaf mzyan") is Script.ARABIZI
        assert dominant_script("مرحبا كيف الحال") is Script.ARABIC

    def test_dominant_script_of_empty_text(self):
        assert dominant_script("") is Script.UNKNOWN

    def test_dominant_script_is_deterministic(self):
        text = "le wach"
        assert dominant_script(text) == dominant_script(text)

    def test_mixed_script_sentence(self):
        text = "salam خويا, wach l rendez-vous dyal today ok?"
        scripts = {token.script for token in detect(text)}
        assert Script.ARABIC in scripts
        assert Script.ARABIZI in scripts

    def test_empty_text(self):
        assert detect("") == []


class TestWordLexicon:
    """Character mapping cannot recover unwritten short vowels; the lexicon can."""

    @pytest.mark.parametrize(
        ("arabizi", "arabic"),
        [
            ("salam", "سلام"),
            ("wach", "واش"),
            ("kayn", "كاين"),
            ("chi", "شي"),
            ("dyal", "ديال"),
            ("bzaf", "بزاف"),
            ("chkoun", "شكون"),
            ("kifach", "كيفاش"),
            ("3afak", "عفاك"),
            ("bghit", "بغيت"),
        ],
    )
    def test_known_words_use_their_settled_spelling(self, arabizi, arabic):
        assert transliterate(arabizi) == arabic

    def test_lexicon_beats_the_character_mapping(self):
        """'salam' letter by letter gives سالام; the correct form is سلام."""
        assert transliterate("salam") == "سلام"
        assert transliterate("salam") != "سالام"

    def test_spelling_variants_converge(self):
        assert transliterate("wach") == transliterate("wash")
        assert transliterate("chkoun") == transliterate("shkoun")
        assert transliterate("dyal") == transliterate("dial")

    def test_lookup_is_case_insensitive(self):
        assert transliterate("Salam") == transliterate("salam")

    def test_unknown_words_still_fall_back_to_characters(self):
        out = transliterate("zzzz")
        assert out and all("؀" <= char <= "ۿ" for char in out)

    def test_words_and_fallback_mix_in_one_sentence(self):
        out = transliterate("salam khouya labghina")
        assert out.startswith("سلام")
        assert "خويا" in out

    def test_multiword_expansions_are_allowed(self):
        """Some single arabizi tokens are several Arabic words."""
        assert transliterate("mabghitch") == "ما بغيتش"
        assert transliterate("hamdullah") == "الحمد لله"

    def test_spacing_around_looked_up_words_is_preserved(self):
        assert transliterate("salam  3lik") == "سلام  عليك"

    def test_punctuation_next_to_a_known_word(self):
        assert transliterate("salam,") == "سلام,"

    def test_protected_spans_still_win(self):
        assert "https://a.example" in transliterate("salam https://a.example")

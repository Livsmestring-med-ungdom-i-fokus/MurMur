"""Tests for music_ai_core.vocal — formant-based vocal synthesis."""

import pytest
import numpy as np
from music_ai_core.vocal import (
    VOWEL_FORMANTS,
    VOWELS,
    VocalSynthesizer,
    solfege_to_syllables,
)


class TestVowelFormants:
    def test_five_vowels_defined(self):
        assert set(VOWELS) == {"A", "E", "I", "O", "U"}

    def test_each_vowel_has_three_formants(self):
        for vowel, formants in VOWEL_FORMANTS.items():
            assert len(formants) == 3, f"{vowel} should have 3 formants"

    def test_formant_frequencies_positive(self):
        for vowel, formants in VOWEL_FORMANTS.items():
            for freq, bw in formants:
                assert freq > 0, f"{vowel}: formant frequency must be positive"
                assert bw > 0, f"{vowel}: bandwidth must be positive"


class TestVocalSynthesizer:
    def setup_method(self):
        self.synth = VocalSynthesizer(sample_rate=22050)

    def test_synthesize_vowel_returns_float32(self):
        audio = self.synth.synthesize_vowel("A", frequency=440.0, duration=0.1)
        assert audio.dtype == np.float32

    def test_synthesize_vowel_correct_length(self):
        duration = 0.2
        audio = self.synth.synthesize_vowel("E", frequency=330.0, duration=duration)
        expected = int(22050 * duration)
        assert len(audio) == expected

    def test_synthesize_all_vowels(self):
        for vowel in VOWELS:
            audio = self.synth.synthesize_vowel(vowel, frequency=220.0, duration=0.05)
            assert len(audio) > 0
            assert audio.dtype == np.float32

    def test_case_insensitive_vowel(self):
        upper = self.synth.synthesize_vowel("A", frequency=440.0, duration=0.1)
        lower = self.synth.synthesize_vowel("a", frequency=440.0, duration=0.1)
        np.testing.assert_array_equal(upper, lower)

    def test_unknown_vowel_raises(self):
        with pytest.raises(ValueError, match="Unknown vowel"):
            self.synth.synthesize_vowel("Z", frequency=440.0, duration=0.1)

    def test_no_vibrato_is_valid(self):
        audio = self.synth.synthesize_vowel("O", frequency=220.0, duration=0.1,
                                             vibrato_rate=0.0, vibrato_depth=0.0)
        assert len(audio) > 0

    def test_synthesize_vocal_line(self):
        syllables = ["do", "re", "mi"]
        frequencies = [261.63, 293.66, 329.63]
        durations = [0.1, 0.1, 0.1]
        audio = self.synth.synthesize_vocal_line(syllables, frequencies, durations)
        expected_len = int(22050 * sum(durations))
        assert len(audio) == pytest.approx(expected_len, abs=10)

    def test_vocal_line_with_rest(self):
        syllables = ["do", "---", "mi"]
        frequencies = [261.63, 0.0, 329.63]
        durations = [0.1, 0.1, 0.1]
        audio = self.synth.synthesize_vocal_line(syllables, frequencies, durations)
        assert len(audio) > 0

    def test_vocal_line_length_mismatch_raises(self):
        with pytest.raises(ValueError):
            self.synth.synthesize_vocal_line(["do", "re"], [261.63], [0.1, 0.1])

    def test_vocal_line_empty(self):
        audio = self.synth.synthesize_vocal_line([], [], [])
        assert isinstance(audio, np.ndarray)
        assert len(audio) == 0

    def test_add_vibrato_same_length(self):
        audio = self.synth.synthesize_vowel("I", 440.0, 0.1)
        result = self.synth.add_vibrato(audio)
        assert len(result) == len(audio)

    def test_add_chorus_same_length(self):
        audio = self.synth.synthesize_vowel("U", 220.0, 0.1)
        result = self.synth.add_chorus(audio)
        assert len(result) == len(audio)

    def test_add_breath_same_length(self):
        audio = self.synth.synthesize_vowel("A", 440.0, 0.2)
        result = self.synth.add_breath(audio)
        assert len(result) == len(audio)

    def test_de_esser_same_length(self):
        audio = self.synth.synthesize_vowel("E", 440.0, 0.1)
        result = self.synth.de_esser(audio)
        assert len(result) == len(audio)

    def test_de_esser_attenuates_loud_samples(self):
        audio = np.ones(1000, dtype=np.float32)
        result = self.synth.de_esser(audio, threshold=0.5)
        assert float(np.max(np.abs(result))) <= 0.5 + 1e-4


class TestSolfegeToSyllables:
    def test_basic_mapping(self):
        syllables, vowels = solfege_to_syllables(["do", "re", "mi"])
        assert syllables == ["do", "re", "mi"]
        assert vowels == ["O", "E", "I"]

    def test_full_scale(self):
        scale = ["do", "re", "mi", "fa", "sol", "la", "si"]
        syllables, vowels = solfege_to_syllables(scale)
        assert len(syllables) == 7
        assert len(vowels) == 7

    def test_case_insensitive(self):
        syllables1, _ = solfege_to_syllables(["DO", "RE"])
        syllables2, _ = solfege_to_syllables(["do", "re"])
        assert syllables1 == syllables2

    def test_unknown_syllable_falls_back(self):
        syllables, vowels = solfege_to_syllables(["xyz"])
        assert syllables == ["xyz"]
        assert vowels == ["A"]

    def test_empty_input(self):
        syllables, vowels = solfege_to_syllables([])
        assert syllables == []
        assert vowels == []

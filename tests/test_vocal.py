"""Tests for music_ai_core.vocal – formant synthesis and effects."""

import numpy as np
import pytest

from music_ai_core.vocal import (
    VOWEL_FORMANTS,
    VocalSynthesizer,
    solfege_to_syllables,
)


SR = 22050  # low sample rate for fast tests


# ---------------------------------------------------------------------------
# VOWEL_FORMANTS
# ---------------------------------------------------------------------------

class TestVowelFormants:
    def test_all_five_vowels_present(self):
        for v in ("A", "E", "I", "O", "U"):
            assert v in VOWEL_FORMANTS

    def test_each_vowel_has_three_formants(self):
        for v, formants in VOWEL_FORMANTS.items():
            assert len(formants) == 3, f"Vowel {v} should have 3 formants"

    def test_formant_frequencies_positive(self):
        for v, formants in VOWEL_FORMANTS.items():
            for f0, bw in formants:
                assert f0 > 0
                assert bw > 0


# ---------------------------------------------------------------------------
# VocalSynthesizer – synthesize_vowel
# ---------------------------------------------------------------------------

class TestSynthesizeVowel:
    @pytest.fixture
    def synth(self):
        return VocalSynthesizer(sample_rate=SR)

    def test_returns_numpy_array(self, synth):
        audio = synth.synthesize_vowel("A", 220.0, 0.1)
        assert isinstance(audio, np.ndarray)

    def test_dtype_float32(self, synth):
        audio = synth.synthesize_vowel("E", 440.0, 0.1)
        assert audio.dtype == np.float32

    def test_length_matches_duration(self, synth):
        dur = 0.2
        audio = synth.synthesize_vowel("I", 330.0, dur)
        expected = int(SR * dur)
        assert len(audio) == expected

    def test_all_vowels_produce_audio(self, synth):
        for vowel in ("A", "E", "I", "O", "U"):
            audio = synth.synthesize_vowel(vowel, 440.0, 0.05)
            assert len(audio) > 0

    def test_lowercase_vowel_accepted(self, synth):
        audio = synth.synthesize_vowel("a", 440.0, 0.05)
        assert len(audio) > 0

    def test_invalid_vowel_raises(self, synth):
        with pytest.raises(ValueError, match="Unknown vowel"):
            synth.synthesize_vowel("X", 440.0, 0.1)

    def test_no_vibrato(self, synth):
        audio = synth.synthesize_vowel("O", 440.0, 0.1, vibrato_rate=0, vibrato_depth=0)
        assert len(audio) > 0


# ---------------------------------------------------------------------------
# VocalSynthesizer – synthesize_vocal_line
# ---------------------------------------------------------------------------

class TestSynthesizeVocalLine:
    @pytest.fixture
    def synth(self):
        return VocalSynthesizer(sample_rate=SR)

    def test_basic_line(self, synth):
        audio = synth.synthesize_vocal_line(
            syllables=["do", "re", "mi"],
            frequencies=[261.0, 293.0, 329.0],
            durations=[0.1, 0.1, 0.1],
        )
        assert audio.dtype == np.float32
        assert len(audio) == pytest.approx(int(SR * 0.3), abs=5)

    def test_rest_on_no_vowel(self, synth):
        audio = synth.synthesize_vocal_line(
            syllables=["nnn"],
            frequencies=[440.0],
            durations=[0.1],
        )
        # Should be silence (zeros or near zero)
        assert np.max(np.abs(audio)) < 1e-6

    def test_rest_on_zero_frequency(self, synth):
        audio = synth.synthesize_vocal_line(
            syllables=["la"],
            frequencies=[0.0],
            durations=[0.1],
        )
        assert np.max(np.abs(audio)) < 1e-6

    def test_mismatched_lengths_raise(self, synth):
        with pytest.raises(ValueError):
            synth.synthesize_vocal_line(
                syllables=["do", "re"],
                frequencies=[261.0],
                durations=[0.1, 0.1],
            )

    def test_empty_input_returns_empty(self, synth):
        audio = synth.synthesize_vocal_line([], [], [])
        assert len(audio) == 0


# ---------------------------------------------------------------------------
# VocalSynthesizer – effects
# ---------------------------------------------------------------------------

class TestVocalEffects:
    @pytest.fixture
    def synth(self):
        return VocalSynthesizer(sample_rate=SR)

    @pytest.fixture
    def sample_audio(self, synth):
        return synth.synthesize_vowel("A", 440.0, 0.2)

    def test_add_vibrato_preserves_length(self, synth, sample_audio):
        out = synth.add_vibrato(sample_audio)
        assert len(out) == len(sample_audio)

    def test_add_vibrato_dtype(self, synth, sample_audio):
        out = synth.add_vibrato(sample_audio)
        assert out.dtype == np.float32

    def test_add_chorus_preserves_length(self, synth, sample_audio):
        out = synth.add_chorus(sample_audio)
        assert len(out) == len(sample_audio)

    def test_add_chorus_mix_zero_returns_dry(self, synth, sample_audio):
        out = synth.add_chorus(sample_audio, mix=0.0)
        np.testing.assert_array_almost_equal(out, sample_audio, decimal=5)

    def test_add_breath_preserves_length(self, synth, sample_audio):
        out = synth.add_breath(sample_audio)
        assert len(out) == len(sample_audio)

    def test_de_esser_reduces_peaks(self, synth, sample_audio):
        loud = (sample_audio * 3.0).astype(np.float32)
        out = synth.de_esser(loud, threshold=0.4)
        assert float(np.max(np.abs(out))) <= 0.41


# ---------------------------------------------------------------------------
# solfege_to_syllables
# ---------------------------------------------------------------------------

class TestSolfegeToSyllables:
    def test_basic_mapping(self):
        syls, vows = solfege_to_syllables(["do", "re", "mi"])
        assert syls == ["do", "re", "mi"]
        assert vows == ["O", "E", "I"]

    def test_full_scale(self):
        scale = ["do", "re", "mi", "fa", "sol", "la", "si", "ti"]
        syls, vows = solfege_to_syllables(scale)
        assert len(syls) == 8
        assert len(vows) == 8

    def test_unknown_syllable_defaults_to_a(self):
        _, vows = solfege_to_syllables(["xyz"])
        assert vows == ["A"]

    def test_empty_input(self):
        syls, vows = solfege_to_syllables([])
        assert syls == []
        assert vows == []

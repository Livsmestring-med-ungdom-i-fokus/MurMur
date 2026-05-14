"""Tests for music_ai_core.dance – drum synthesizer and beat generator."""

import numpy as np
import pytest

from music_ai_core.dance import (
    DANCE_GENRES,
    DrumSynthesizer,
    BeatGenerator,
    list_genres,
    genre_description,
)


# ---------------------------------------------------------------------------
# DANCE_GENRES registry
# ---------------------------------------------------------------------------

class TestDanceGenres:
    def test_known_genres_present(self):
        for name in ("house", "techno", "hip_hop", "trap", "pop"):
            assert name in DANCE_GENRES

    def test_genre_bpm_range_valid(self):
        for name, genre in DANCE_GENRES.items():
            lo, hi = genre.bpm_range
            assert lo < hi, f"{name}: bpm_range lower bound must be < upper bound"
            assert genre.bpm_range[0] <= genre.default_bpm <= genre.bpm_range[1]

    def test_genre_time_signature(self):
        for name, genre in DANCE_GENRES.items():
            num, denom = genre.time_signature
            assert num > 0
            assert denom > 0


# ---------------------------------------------------------------------------
# DrumSynthesizer
# ---------------------------------------------------------------------------

class TestDrumSynthesizer:
    @pytest.fixture
    def synth(self):
        return DrumSynthesizer(sample_rate=44100)

    def test_kick_shape(self, synth):
        audio = synth.kick()
        assert audio.ndim == 1
        assert audio.dtype == np.float32
        assert len(audio) > 0

    def test_snare_normalised(self, synth):
        audio = synth.snare()
        assert np.max(np.abs(audio)) <= 1.0

    def test_hihat_closed_shorter_than_open(self, synth):
        closed = synth.hihat_closed()
        open_ = synth.hihat_open()
        assert len(closed) < len(open_)

    def test_clap_is_float32(self, synth):
        audio = synth.clap()
        assert audio.dtype == np.float32

    def test_hit_dispatch_all_voices(self, synth):
        for voice in ("kick", "snare", "hihat_closed", "hihat_open", "clap"):
            audio = synth.hit(voice)
            assert len(audio) > 0

    def test_hit_invalid_voice_raises(self, synth):
        with pytest.raises(ValueError, match="Unknown drum voice"):
            synth.hit("cowbell")


# ---------------------------------------------------------------------------
# BeatGenerator
# ---------------------------------------------------------------------------

class TestBeatGenerator:
    @pytest.fixture
    def generator(self):
        return BeatGenerator(sample_rate=22050)

    def test_generate_bar_returns_dict(self, generator):
        tracks = generator.generate_bar(genre="house", bars=1)
        assert isinstance(tracks, dict)
        assert len(tracks) > 0

    def test_generate_bar_all_voices_present(self, generator):
        tracks = generator.generate_bar(genre="pop")
        for voice in ("kick", "snare", "hihat_closed", "hihat_open", "clap"):
            assert voice in tracks

    def test_generate_bar_audio_is_float32(self, generator):
        tracks = generator.generate_bar(genre="techno")
        for voice, audio in tracks.items():
            assert audio.dtype == np.float32, f"{voice} audio dtype wrong"

    def test_two_bars_is_twice_as_long_as_one(self, generator):
        one_bar = generator.generate_bar(genre="hip_hop", bars=1)
        two_bars = generator.generate_bar(genre="hip_hop", bars=2)
        for voice in one_bar:
            assert len(two_bars[voice]) == pytest.approx(
                len(one_bar[voice]) * 2, abs=1
            )

    def test_bpm_override(self, generator):
        """Higher BPM should produce a shorter bar."""
        slow = generator.generate_bar(genre="house", bpm=60, bars=1)
        fast = generator.generate_bar(genre="house", bpm=120, bars=1)
        for voice in slow:
            assert len(fast[voice]) < len(slow[voice])

    def test_invalid_genre_raises(self, generator):
        with pytest.raises(ValueError, match="Unknown genre"):
            generator.generate_bar(genre="polka")

    def test_humanize_does_not_change_length(self, generator):
        normal = generator.generate_bar(genre="house", bars=1, humanize=0.0)
        humanized = generator.generate_bar(genre="house", bars=1, humanize=0.5)
        for voice in normal:
            assert len(normal[voice]) == len(humanized[voice])

    def test_get_genre_info_returns_metadata(self, generator):
        info = generator.get_genre_info("trap")
        assert info.name == "Trap"

    def test_get_genre_info_invalid_raises(self, generator):
        with pytest.raises(ValueError, match="Unknown genre"):
            generator.get_genre_info("polka")


# ---------------------------------------------------------------------------
# Convenience helpers
# ---------------------------------------------------------------------------

class TestDanceHelpers:
    def test_list_genres_sorted(self):
        genres = list_genres()
        assert genres == sorted(genres)
        assert "house" in genres

    def test_genre_description_contains_name(self):
        desc = genre_description("house")
        assert "House" in desc

    def test_genre_description_unknown(self):
        desc = genre_description("polka")
        assert "Unknown" in desc

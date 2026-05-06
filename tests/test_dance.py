"""Tests for music_ai_core.dance — drum beat generator."""

import pytest
import numpy as np
from music_ai_core.dance import (
    DANCE_GENRES,
    DRUM_VOICES,
    PATTERNS,
    DrumSynthesizer,
    BeatGenerator,
    list_genres,
    genre_description,
)


class TestDanceGenres:
    def test_all_genres_present(self):
        expected = {"house", "techno", "drum_and_bass", "hip_hop", "trap",
                    "reggaeton", "afrobeats", "pop"}
        assert set(DANCE_GENRES.keys()) == expected

    def test_bpm_range_valid(self):
        for name, genre in DANCE_GENRES.items():
            lo, hi = genre.bpm_range
            assert lo < hi, f"{name}: min BPM must be less than max BPM"
            assert genre.default_bpm in range(lo, hi + 1), \
                f"{name}: default_bpm {genre.default_bpm} outside range ({lo}, {hi})"

    def test_time_signature_4_4(self):
        for name, genre in DANCE_GENRES.items():
            assert genre.time_signature == (4, 4), f"{name} should be 4/4"

    def test_tags_is_list(self):
        for name, genre in DANCE_GENRES.items():
            assert isinstance(genre.tags, list)


class TestPatterns:
    def test_all_genres_have_patterns(self):
        for genre in DANCE_GENRES:
            assert genre in PATTERNS, f"Missing pattern for {genre}"

    def test_patterns_have_16_steps(self):
        for genre, voices in PATTERNS.items():
            for voice, steps in voices.items():
                assert len(steps) == 16, \
                    f"{genre}/{voice} has {len(steps)} steps (expected 16)"

    def test_patterns_contain_binary_values(self):
        for genre, voices in PATTERNS.items():
            for voice, steps in voices.items():
                for val in steps:
                    assert val in (0, 1), \
                        f"{genre}/{voice} contains non-binary value {val}"


class TestDrumSynthesizer:
    def setup_method(self):
        self.synth = DrumSynthesizer(sample_rate=22050)

    def test_kick_returns_float32(self):
        audio = self.synth.kick(duration=0.1)
        assert audio.dtype == np.float32

    def test_kick_length(self):
        duration = 0.1
        audio = self.synth.kick(duration=duration)
        expected = int(22050 * duration)
        assert len(audio) == expected

    def test_snare_returns_audio(self):
        audio = self.synth.snare()
        assert len(audio) > 0
        assert audio.dtype == np.float32

    def test_hihat_closed_is_short(self):
        audio = self.synth.hihat_closed()
        assert len(audio) > 0

    def test_hihat_open_is_longer_than_closed(self):
        closed = self.synth.hihat_closed()
        opened = self.synth.hihat_open()
        assert len(opened) > len(closed)

    def test_clap_returns_audio(self):
        audio = self.synth.clap()
        assert len(audio) > 0
        assert audio.dtype == np.float32

    def test_normalize_peak(self):
        audio = self.synth.kick()
        assert np.max(np.abs(audio)) <= 1.0

    def test_hit_dispatches_all_voices(self):
        for voice in DRUM_VOICES:
            audio = self.synth.hit(voice)
            assert isinstance(audio, np.ndarray)
            assert len(audio) > 0

    def test_hit_unknown_voice_raises(self):
        with pytest.raises(ValueError, match="Unknown drum voice"):
            self.synth.hit("cowbell")


class TestBeatGenerator:
    def setup_method(self):
        self.gen = BeatGenerator(sample_rate=22050)

    def test_generate_bar_returns_all_voices(self):
        tracks = self.gen.generate_bar(genre="house")
        for voice in DRUM_VOICES:
            assert voice in tracks

    def test_generate_bar_audio_is_float32(self):
        tracks = self.gen.generate_bar(genre="pop")
        for voice, audio in tracks.items():
            assert audio.dtype == np.float32, f"{voice} is not float32"

    def test_generate_bar_audio_is_non_trivial(self):
        tracks = self.gen.generate_bar(genre="techno")
        total_energy = sum(np.sum(np.abs(a)) for a in tracks.values())
        assert total_energy > 0

    def test_generate_two_bars(self):
        one_bar = self.gen.generate_bar(genre="hip_hop", bars=1)
        two_bars = self.gen.generate_bar(genre="hip_hop", bars=2)
        for voice in DRUM_VOICES:
            assert len(two_bars[voice]) == pytest.approx(len(one_bar[voice]) * 2, rel=0.01)

    def test_custom_bpm(self):
        tracks = self.gen.generate_bar(genre="house", bpm=100)
        assert len(tracks) == len(DRUM_VOICES)

    def test_humanize_runs_without_error(self):
        tracks = self.gen.generate_bar(genre="trap", humanize=0.5)
        assert len(tracks) == len(DRUM_VOICES)

    def test_unknown_genre_raises(self):
        with pytest.raises(ValueError, match="Unknown genre"):
            self.gen.generate_bar(genre="polka")

    def test_get_genre_info(self):
        info = self.gen.get_genre_info("techno")
        assert info.name == "Techno"

    def test_get_genre_info_unknown_raises(self):
        with pytest.raises(ValueError):
            self.gen.get_genre_info("polka")

    def test_all_genres_generate(self):
        for genre in DANCE_GENRES:
            tracks = self.gen.generate_bar(genre=genre)
            assert len(tracks) == len(DRUM_VOICES)


class TestListHelpers:
    def test_list_genres_sorted(self):
        genres = list_genres()
        assert genres == sorted(genres)
        assert len(genres) > 0

    def test_genre_description_returns_string(self):
        desc = genre_description("house")
        assert isinstance(desc, str)
        assert "House" in desc

    def test_genre_description_unknown(self):
        desc = genre_description("polka")
        assert "Unknown" in desc

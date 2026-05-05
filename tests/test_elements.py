"""Tests for music_ai_core.elements — musical building blocks."""

import pytest
from music_ai_core.elements import (
    NOTE_FREQUENCIES,
    ALL_NOTE_NAMES,
    SCALE_PATTERNS,
    CHORD_INTERVALS,
    RHYTHM_PATTERNS,
    get_scale,
    get_chord,
    scale_frequencies,
    chord_frequencies,
    melody_from_scale,
    interval_name,
    list_scales,
    list_chords,
    list_rhythms,
    scale_rhythm_to_bpm,
)


class TestNoteFrequencies:
    def test_a4_is_440hz(self):
        assert NOTE_FREQUENCIES["A4"] == pytest.approx(440.0, rel=1e-4)

    def test_a5_is_octave_above_a4(self):
        assert NOTE_FREQUENCIES["A5"] == pytest.approx(NOTE_FREQUENCIES["A4"] * 2, rel=1e-4)

    def test_a3_is_octave_below_a4(self):
        assert NOTE_FREQUENCIES["A3"] == pytest.approx(NOTE_FREQUENCIES["A4"] / 2, rel=1e-4)

    def test_c4_frequency(self):
        # C4 (middle C) ≈ 261.63 Hz
        assert NOTE_FREQUENCIES["C4"] == pytest.approx(261.63, rel=1e-2)

    def test_all_notes_have_positive_frequency(self):
        for note, freq in NOTE_FREQUENCIES.items():
            assert freq > 0, f"{note} has non-positive frequency"

    def test_chromatic_notes_all_present(self):
        for octave in range(9):
            for name in ALL_NOTE_NAMES:
                assert f"{name}{octave}" in NOTE_FREQUENCIES


class TestAllNoteNames:
    def test_twelve_chromatic_notes(self):
        assert len(ALL_NOTE_NAMES) == 12

    def test_starts_with_c(self):
        assert ALL_NOTE_NAMES[0] == "C"

    def test_contains_sharps(self):
        assert "C#" in ALL_NOTE_NAMES
        assert "F#" in ALL_NOTE_NAMES


class TestGetScale:
    def test_c_major_has_seven_notes(self):
        scale = get_scale("C", "major", octave=4)
        assert len(scale) == 7

    def test_c_major_root_is_c4(self):
        scale = get_scale("C", "major", octave=4)
        assert scale[0][0] == "C4"

    def test_c_major_frequencies_ascending(self):
        freqs = scale_frequencies("C", "major", octave=4)
        assert freqs == sorted(freqs)

    def test_pentatonic_major_has_five_notes(self):
        scale = get_scale("A", "pentatonic_major", octave=3)
        assert len(scale) == 5

    def test_chromatic_scale_has_twelve_notes(self):
        scale = get_scale("C", "chromatic", octave=4)
        assert len(scale) == 12

    def test_invalid_root_raises(self):
        with pytest.raises(ValueError, match="Unknown root note"):
            get_scale("H", "major")

    def test_invalid_scale_raises(self):
        with pytest.raises(ValueError, match="Unknown scale"):
            get_scale("C", "nonexistent_scale")

    def test_all_scale_patterns_buildable(self):
        for scale_name in SCALE_PATTERNS:
            result = get_scale("C", scale_name, octave=4)
            assert len(result) == len(SCALE_PATTERNS[scale_name])


class TestGetChord:
    def test_major_triad_has_three_notes(self):
        chord = get_chord("C", "major", octave=4)
        assert len(chord) == 3

    def test_major7_has_four_notes(self):
        chord = get_chord("C", "major7", octave=4)
        assert len(chord) == 4

    def test_major9_has_five_notes(self):
        chord = get_chord("C", "major9", octave=4)
        assert len(chord) == 5

    def test_power_chord_has_two_notes(self):
        chord = get_chord("E", "power", octave=2)
        assert len(chord) == 2

    def test_chord_frequencies_positive(self):
        freqs = chord_frequencies("A", "minor", octave=4)
        assert all(f > 0 for f in freqs)

    def test_invalid_root_raises(self):
        with pytest.raises(ValueError):
            get_chord("Z", "major")

    def test_invalid_chord_type_raises(self):
        with pytest.raises(ValueError):
            get_chord("C", "nonexistent_chord")


class TestIntervalName:
    def test_unison_is_zero(self):
        assert interval_name(0) == "unison"

    def test_perfect_fifth_is_seven(self):
        assert interval_name(7) == "perfect_fifth"

    def test_wraps_around_octave(self):
        # 12 semitones normalises to 0 (unison) via % 12
        assert interval_name(12) == interval_name(0)

    def test_unknown_semitones_returns_string(self):
        result = interval_name(13)
        assert "13" in result or isinstance(result, str)


class TestRhythm:
    def test_quarter_notes_has_four_entries(self):
        assert len(RHYTHM_PATTERNS["quarter_notes"]) == 4

    def test_eighth_notes_has_eight_entries(self):
        assert len(RHYTHM_PATTERNS["eighth_notes"]) == 8

    def test_scale_to_bpm_faster_gives_shorter_durations(self):
        at_120 = scale_rhythm_to_bpm("quarter_notes", 120)
        at_240 = scale_rhythm_to_bpm("quarter_notes", 240)
        assert sum(at_240) < sum(at_120)

    def test_invalid_rhythm_raises(self):
        with pytest.raises(ValueError):
            scale_rhythm_to_bpm("nonexistent", 120)


class TestMelodyFromScale:
    def test_returns_list_of_tuples(self):
        melody = melody_from_scale("C", "major", octave=4)
        assert isinstance(melody, list)
        assert all(isinstance(item, tuple) and len(item) == 2 for item in melody)

    def test_all_frequencies_positive(self):
        melody = melody_from_scale("G", "minor", octave=3)
        assert all(freq > 0 for freq, _ in melody)

    def test_all_durations_positive(self):
        melody = melody_from_scale("D", "major", octave=4, bpm=100)
        assert all(dur > 0 for _, dur in melody)


class TestListHelpers:
    def test_list_scales_returns_sorted_list(self):
        scales = list_scales()
        assert scales == sorted(scales)
        assert len(scales) > 0

    def test_list_chords_returns_sorted_list(self):
        chords = list_chords()
        assert chords == sorted(chords)
        assert len(chords) > 0

    def test_list_rhythms_returns_sorted_list(self):
        rhythms = list_rhythms()
        assert rhythms == sorted(rhythms)
        assert len(rhythms) > 0

"""Tests for music_ai_core.elements – musical building blocks."""

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
    scale_rhythm_to_bpm,
    list_scales,
    list_chords,
    list_rhythms,
)


# ---------------------------------------------------------------------------
# NOTE_FREQUENCIES
# ---------------------------------------------------------------------------

class TestNoteFrequencies:
    def test_a4_is_440hz(self):
        assert NOTE_FREQUENCIES["A4"] == pytest.approx(440.0, rel=1e-4)

    def test_c4_is_approx_261hz(self):
        assert NOTE_FREQUENCIES["C4"] == pytest.approx(261.6256, rel=1e-3)

    def test_frequencies_are_positive(self):
        for key, freq in NOTE_FREQUENCIES.items():
            assert freq > 0, f"{key} has non-positive frequency"

    def test_octave_doubles_frequency(self):
        assert NOTE_FREQUENCIES["A5"] == pytest.approx(NOTE_FREQUENCIES["A4"] * 2, rel=1e-4)

    def test_all_12_chromatic_notes_present(self):
        for name in ALL_NOTE_NAMES:
            assert f"{name}4" in NOTE_FREQUENCIES

    def test_note_count(self):
        # 9 octaves × 12 notes = 108 entries
        assert len(NOTE_FREQUENCIES) == 108


# ---------------------------------------------------------------------------
# ALL_NOTE_NAMES
# ---------------------------------------------------------------------------

class TestAllNoteNames:
    def test_has_12_names(self):
        assert len(ALL_NOTE_NAMES) == 12

    def test_starts_with_c(self):
        assert ALL_NOTE_NAMES[0] == "C"

    def test_contains_sharps(self):
        assert "C#" in ALL_NOTE_NAMES
        assert "F#" in ALL_NOTE_NAMES


# ---------------------------------------------------------------------------
# interval_name
# ---------------------------------------------------------------------------

class TestIntervalName:
    def test_unison(self):
        assert interval_name(0) == "unison"

    def test_octave(self):
        # 12 % 12 == 0, which maps to "unison" in the reverse lookup
        assert interval_name(12) == "unison"

    def test_perfect_fifth(self):
        assert interval_name(7) == "perfect_fifth"

    def test_minor_third(self):
        assert interval_name(3) == "minor_third"

    def test_wraparound(self):
        # 13 semitones wraps to 1 (minor_second)
        assert interval_name(13) == "minor_second"

    def test_unknown_returns_semitone_label(self):
        # No standard name for e.g. 15; normalises to 3 → minor_third
        assert interval_name(15) == "minor_third"


# ---------------------------------------------------------------------------
# get_scale / scale_frequencies
# ---------------------------------------------------------------------------

class TestGetScale:
    def test_c_major_length(self):
        scale = get_scale("C", "major", octave=4)
        assert len(scale) == 7

    def test_c_major_first_note(self):
        scale = get_scale("C", "major", octave=4)
        note, freq = scale[0]
        assert note == "C4"
        assert freq == pytest.approx(NOTE_FREQUENCIES["C4"], rel=1e-6)

    def test_pentatonic_has_5_notes(self):
        scale = get_scale("A", "pentatonic_minor", octave=4)
        assert len(scale) == 5

    def test_chromatic_has_12_notes(self):
        scale = get_scale("C", "chromatic", octave=4)
        assert len(scale) == 12

    def test_invalid_root_raises(self):
        with pytest.raises(ValueError, match="Unknown root note"):
            get_scale("X", "major")

    def test_invalid_scale_raises(self):
        with pytest.raises(ValueError, match="Unknown scale"):
            get_scale("C", "nonexistent")

    def test_scale_frequencies_length_matches(self):
        freqs = scale_frequencies("D", "major", octave=3)
        assert len(freqs) == len(get_scale("D", "major", octave=3))

    def test_scale_frequencies_are_floats(self):
        for freq in scale_frequencies("G", "minor"):
            assert isinstance(freq, float)


# ---------------------------------------------------------------------------
# get_chord / chord_frequencies
# ---------------------------------------------------------------------------

class TestGetChord:
    def test_major_triad_has_3_notes(self):
        chord = get_chord("C", "major", octave=4)
        assert len(chord) == 3

    def test_dominant7_has_4_notes(self):
        chord = get_chord("G", "dominant7", octave=4)
        assert len(chord) == 4

    def test_major9_has_5_notes(self):
        chord = get_chord("C", "major9", octave=4)
        assert len(chord) == 5

    def test_power_chord_has_2_notes(self):
        chord = get_chord("E", "power", octave=3)
        assert len(chord) == 2

    def test_invalid_root_raises(self):
        with pytest.raises(ValueError, match="Unknown root"):
            get_chord("Z", "major")

    def test_invalid_chord_type_raises(self):
        with pytest.raises(ValueError, match="Unknown chord type"):
            get_chord("C", "bluesxyz")

    def test_chord_frequencies_positive(self):
        for freq in chord_frequencies("A", "minor"):
            assert freq > 0


# ---------------------------------------------------------------------------
# RHYTHM_PATTERNS / scale_rhythm_to_bpm / melody_from_scale
# ---------------------------------------------------------------------------

class TestRhythm:
    def test_quarter_notes_total_2_seconds_at_120bpm(self):
        pattern = RHYTHM_PATTERNS["quarter_notes"]
        assert sum(pattern) == pytest.approx(2.0, rel=1e-6)

    def test_scaling_at_240bpm_halves_durations(self):
        scaled = scale_rhythm_to_bpm("quarter_notes", 240)
        base = RHYTHM_PATTERNS["quarter_notes"]
        for s, b in zip(scaled, base):
            assert s == pytest.approx(b * 0.5, rel=1e-6)

    def test_scaling_at_60bpm_doubles_durations(self):
        scaled = scale_rhythm_to_bpm("eighth_notes", 60)
        base = RHYTHM_PATTERNS["eighth_notes"]
        for s, b in zip(scaled, base):
            assert s == pytest.approx(b * 2.0, rel=1e-6)

    def test_invalid_rhythm_raises(self):
        with pytest.raises(ValueError, match="Unknown rhythm"):
            scale_rhythm_to_bpm("nonexistent", 120)


class TestMelodyFromScale:
    def test_returns_pairs(self):
        melody = melody_from_scale("C", "major")
        assert all(isinstance(freq, float) and isinstance(dur, float)
                   for freq, dur in melody)

    def test_length_matches_scale(self):
        melody = melody_from_scale("C", "pentatonic_major")
        assert len(melody) == 5


# ---------------------------------------------------------------------------
# List helpers
# ---------------------------------------------------------------------------

class TestListHelpers:
    def test_list_scales_returns_sorted(self):
        scales = list_scales()
        assert scales == sorted(scales)
        assert "major" in scales
        assert "minor" in scales

    def test_list_chords_returns_sorted(self):
        chords = list_chords()
        assert chords == sorted(chords)
        assert "major" in chords

    def test_list_rhythms_returns_sorted(self):
        rhythms = list_rhythms()
        assert rhythms == sorted(rhythms)
        assert "quarter_notes" in rhythms

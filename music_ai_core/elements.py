"""
Elements Module – Musical Building Blocks

Provides the fundamental musical primitives needed by all other modules:
- Note name → frequency lookup (9 octaves, 12-tone equal temperament)
- Scale generator (major, minor, pentatonic, blues, dorian, …)
- Chord builder (triads, seventh chords, extended chords)
- Interval helpers
- Rhythm pattern definitions
"""

from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Note / frequency tables
# ---------------------------------------------------------------------------

# Reference: A4 = 440 Hz (MIDI standard 12-TET)
_CHROMATIC = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

NOTE_FREQUENCIES: Dict[str, float] = {}
for _octave in range(9):
    for _semitone, _name in enumerate(_CHROMATIC):
        _midi = (_octave + 1) * 12 + _semitone  # C1 = MIDI 24
        _freq = 440.0 * (2 ** ((_midi - 69) / 12))
        NOTE_FREQUENCIES[f"{_name}{_octave}"] = round(_freq, 4)

# Convenience set: note names without octave
ALL_NOTE_NAMES: List[str] = _CHROMATIC[:]


# ---------------------------------------------------------------------------
# Interval helpers
# ---------------------------------------------------------------------------

INTERVAL_SEMITONES: Dict[str, int] = {
    "unison":       0,
    "minor_second": 1,
    "major_second": 2,
    "minor_third":  3,
    "major_third":  4,
    "perfect_fourth": 5,
    "tritone":      6,
    "perfect_fifth": 7,
    "minor_sixth":  8,
    "major_sixth":  9,
    "minor_seventh": 10,
    "major_seventh": 11,
    "octave":       12,
}


def interval_name(semitones: int) -> str:
    """Return the common interval name for a semitone distance."""
    normalized = semitones % 12
    reverse = {v: k for k, v in INTERVAL_SEMITONES.items()}
    return reverse.get(normalized, f"{semitones}_semitones")


# ---------------------------------------------------------------------------
# Scale generator
# ---------------------------------------------------------------------------

SCALE_PATTERNS: Dict[str, List[int]] = {
    "major":        [0, 2, 4, 5, 7, 9, 11],
    "minor":        [0, 2, 3, 5, 7, 8, 10],
    "pentatonic_major": [0, 2, 4, 7, 9],
    "pentatonic_minor": [0, 3, 5, 7, 10],
    "blues":        [0, 3, 5, 6, 7, 10],
    "dorian":       [0, 2, 3, 5, 7, 9, 10],
    "phrygian":     [0, 1, 3, 5, 7, 8, 10],
    "lydian":       [0, 2, 4, 6, 7, 9, 11],
    "mixolydian":   [0, 2, 4, 5, 7, 9, 10],
    "locrian":      [0, 1, 3, 5, 6, 8, 10],
    "harmonic_minor": [0, 2, 3, 5, 7, 8, 11],
    "whole_tone":   [0, 2, 4, 6, 8, 10],
    "chromatic":    list(range(12)),
}


def get_scale(root: str, scale_type: str = "major", octave: int = 4) -> List[Tuple[str, float]]:
    """
    Build a scale starting from *root* note.

    Args:
        root: Root note name, e.g. ``"C"``, ``"D#"``
        scale_type: One of the keys in ``SCALE_PATTERNS``
        octave: Starting octave (0-8)

    Returns:
        List of ``(note_name, frequency)`` tuples.
    """
    if root not in ALL_NOTE_NAMES:
        raise ValueError(f"Unknown root note '{root}'. Use one of {ALL_NOTE_NAMES}")
    if scale_type not in SCALE_PATTERNS:
        raise ValueError(f"Unknown scale '{scale_type}'. Available: {list(SCALE_PATTERNS)}")

    root_idx = ALL_NOTE_NAMES.index(root)
    intervals = SCALE_PATTERNS[scale_type]
    result: List[Tuple[str, float]] = []

    for semitones in intervals:
        abs_idx = root_idx + semitones
        cur_octave = octave + abs_idx // 12
        note_name = ALL_NOTE_NAMES[abs_idx % 12]
        freq_key = f"{note_name}{cur_octave}"
        freq = NOTE_FREQUENCIES.get(freq_key, 0.0)
        result.append((freq_key, freq))

    return result


def scale_frequencies(root: str, scale_type: str = "major", octave: int = 4) -> List[float]:
    """Return just the frequencies for a scale (convenient shorthand)."""
    return [freq for _, freq in get_scale(root, scale_type, octave)]


# ---------------------------------------------------------------------------
# Chord builder
# ---------------------------------------------------------------------------

CHORD_INTERVALS: Dict[str, List[int]] = {
    "major":        [0, 4, 7],
    "minor":        [0, 3, 7],
    "diminished":   [0, 3, 6],
    "augmented":    [0, 4, 8],
    "sus2":         [0, 2, 7],
    "sus4":         [0, 5, 7],
    "major7":       [0, 4, 7, 11],
    "dominant7":    [0, 4, 7, 10],
    "minor7":       [0, 3, 7, 10],
    "diminished7":  [0, 3, 6, 9],
    "half_diminished7": [0, 3, 6, 10],
    "major9":       [0, 4, 7, 11, 14],
    "minor9":       [0, 3, 7, 10, 14],
    "add9":         [0, 4, 7, 14],
    "power":        [0, 7],
}


def get_chord(root: str, chord_type: str = "major", octave: int = 4) -> List[Tuple[str, float]]:
    """
    Build a chord.

    Args:
        root: Root note name (e.g. ``"A"``)
        chord_type: One of the keys in ``CHORD_INTERVALS``
        octave: Base octave

    Returns:
        List of ``(note_name, frequency)`` tuples for each chord tone.
    """
    if root not in ALL_NOTE_NAMES:
        raise ValueError(f"Unknown root '{root}'")
    if chord_type not in CHORD_INTERVALS:
        raise ValueError(f"Unknown chord type '{chord_type}'. Available: {list(CHORD_INTERVALS)}")

    root_idx = ALL_NOTE_NAMES.index(root)
    result: List[Tuple[str, float]] = []

    for semitones in CHORD_INTERVALS[chord_type]:
        abs_idx = root_idx + semitones
        cur_octave = octave + abs_idx // 12
        note_name = ALL_NOTE_NAMES[abs_idx % 12]
        freq_key = f"{note_name}{cur_octave}"
        freq = NOTE_FREQUENCIES.get(freq_key, 0.0)
        result.append((freq_key, freq))

    return result


def chord_frequencies(root: str, chord_type: str = "major", octave: int = 4) -> List[float]:
    """Return just the frequencies for a chord."""
    return [freq for _, freq in get_chord(root, chord_type, octave)]


# ---------------------------------------------------------------------------
# Rhythm patterns
# ---------------------------------------------------------------------------

RHYTHM_PATTERNS: Dict[str, List[float]] = {
    # Each entry is a list of note durations in seconds at 120 BPM
    "quarter_notes":    [0.5, 0.5, 0.5, 0.5],
    "eighth_notes":     [0.25] * 8,
    "sixteenth_notes":  [0.125] * 16,
    "dotted_quarter":   [0.75, 0.25, 0.75, 0.25],
    "swing":            [0.333, 0.167] * 4,
    "waltz":            [1.0, 0.5, 0.5, 1.0, 0.5, 0.5],
    "bossa_nova":       [0.375, 0.25, 0.375, 0.5, 0.375, 0.25, 0.375, 0.5],
    "syncopated":       [0.25, 0.5, 0.25, 0.5, 0.25, 0.25],
}


def scale_rhythm_to_bpm(pattern_name: str, bpm: int) -> List[float]:
    """
    Scale a named rhythm pattern to the given BPM.

    Args:
        pattern_name: Key from ``RHYTHM_PATTERNS``
        bpm: Target tempo in beats per minute

    Returns:
        List of note durations (seconds) at the requested BPM.
    """
    if pattern_name not in RHYTHM_PATTERNS:
        raise ValueError(f"Unknown rhythm '{pattern_name}'. Available: {list(RHYTHM_PATTERNS)}")

    scale = 120 / bpm  # patterns are defined at 120 BPM
    return [dur * scale for dur in RHYTHM_PATTERNS[pattern_name]]


# ---------------------------------------------------------------------------
# Melody helpers
# ---------------------------------------------------------------------------

def melody_from_scale(
    root: str,
    scale_type: str = "major",
    octave: int = 4,
    rhythm: str = "quarter_notes",
    bpm: int = 120,
) -> List[Tuple[float, float]]:
    """
    Build a simple ascending scale melody ready for the synthesizer.

    Returns:
        List of ``(frequency, duration_seconds)`` tuples.
    """
    scale_notes = get_scale(root, scale_type, octave)
    durations = scale_rhythm_to_bpm(rhythm, bpm)

    pairs: List[Tuple[float, float]] = []
    for i, (_, freq) in enumerate(scale_notes):
        dur = durations[i % len(durations)]
        pairs.append((freq, dur))

    return pairs


# ---------------------------------------------------------------------------
# Info / introspection
# ---------------------------------------------------------------------------

def list_scales() -> List[str]:
    """Return all available scale names."""
    return sorted(SCALE_PATTERNS.keys())


def list_chords() -> List[str]:
    """Return all available chord type names."""
    return sorted(CHORD_INTERVALS.keys())


def list_rhythms() -> List[str]:
    """Return all available rhythm pattern names."""
    return sorted(RHYTHM_PATTERNS.keys())

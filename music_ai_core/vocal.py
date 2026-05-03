"""
Vocal Module – Formant-based Vocal Synthesis & Effects

Provides:
- Vowel synthesis via formant filtering (five standard vowels: A, E, I, O, U)
- Vocal line builder from syllable/note sequences
- Vibrato and tremolo modulation
- Basic vocal effects (chorus, breath noise, de-esser)
"""

import numpy as np
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Formant tables  (center-frequency, bandwidth) per vowel, three formants
# Reference: Peterson & Barney (1952) "Control Methods Used in a Study of the Vowels"
# JASA 24(2), pp. 175-184 – male speaker averages. https://doi.org/10.1121/1.1906875
# ---------------------------------------------------------------------------

VOWEL_FORMANTS: Dict[str, List[Tuple[float, float]]] = {
    "A": [(800, 80),  (1200, 120), (2500, 200)],
    "E": [(400, 60),  (2200, 130), (2800, 200)],
    "I": [(300, 60),  (2700, 150), (3300, 200)],
    "O": [(500, 70),  (900,  100), (2500, 180)],
    "U": [(350, 60),  (700,  100), (2700, 200)],
}

VOWELS = list(VOWEL_FORMANTS.keys())


class VocalSynthesizer:
    """Synthesize human-like vocal sounds using formant filtering."""

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate

    # ------------------------------------------------------------------
    # Core synthesis
    # ------------------------------------------------------------------

    def synthesize_vowel(
        self,
        vowel: str,
        frequency: float,
        duration: float,
        vibrato_rate: float = 5.5,
        vibrato_depth: float = 0.02,
    ) -> np.ndarray:
        """
        Synthesize a single vowel phoneme.

        Args:
            vowel: One of ``"A"``, ``"E"``, ``"I"``, ``"O"``, ``"U"``
            frequency: Fundamental frequency (Hz) – the pitch of the voice
            duration: Duration in seconds
            vibrato_rate: Vibrato speed in Hz (0 = no vibrato)
            vibrato_depth: Vibrato depth as fraction of fundamental frequency

        Returns:
            Mono audio samples as a float32 numpy array.
        """
        vowel = vowel.upper()
        if vowel not in VOWEL_FORMANTS:
            raise ValueError(f"Unknown vowel '{vowel}'. Use one of {VOWELS}")

        n = int(self.sample_rate * duration)
        t = np.arange(n) / self.sample_rate

        # Carrier: slightly buzzy source (mix of harmonics)
        vibrato = 1.0 + vibrato_depth * np.sin(2 * np.pi * vibrato_rate * t)
        phase = np.cumsum(2 * np.pi * frequency * vibrato / self.sample_rate)

        source = (
            np.sin(phase)
            + 0.5 * np.sin(2 * phase)
            + 0.3 * np.sin(3 * phase)
            + 0.15 * np.sin(4 * phase)
            + 0.1 * np.sin(5 * phase)
        )
        source /= np.max(np.abs(source) + 1e-9)

        # Apply formant resonances
        filtered = self._apply_formants(source, VOWEL_FORMANTS[vowel])

        # ADSR envelope
        env = self._adsr(n, attack=0.05, decay=0.08, sustain=0.8, release=0.15)
        return (filtered * env * 0.25).astype(np.float32)

    def _apply_formants(
        self, signal: np.ndarray, formants: List[Tuple[float, float]]
    ) -> np.ndarray:
        """Boost formant bands with simple bandpass resonators."""
        result = np.zeros_like(signal)
        for f0, bw in formants:
            resonator = self._bandpass_resonator(signal, f0, bw)
            result += resonator
        peak = np.max(np.abs(result) + 1e-9)
        return result / peak

    def _bandpass_resonator(
        self, signal: np.ndarray, center: float, bandwidth: float
    ) -> np.ndarray:
        """Second-order IIR bandpass resonator (Rader–Gold)."""
        w0 = 2 * np.pi * center / self.sample_rate
        r = 1.0 - np.pi * bandwidth / self.sample_rate
        r = max(0.0, min(0.9999, r))

        a1 = -2 * r * np.cos(w0)
        a2 = r ** 2
        b0 = 1.0 - r

        out = np.zeros_like(signal)
        y_prev1 = y_prev2 = 0.0
        for i, x in enumerate(signal):
            y = b0 * x - a1 * y_prev1 - a2 * y_prev2
            out[i] = y
            y_prev2 = y_prev1
            y_prev1 = y
        return out

    def _adsr(
        self,
        n: int,
        attack: float = 0.05,
        decay: float = 0.1,
        sustain: float = 0.8,
        release: float = 0.2,
    ) -> np.ndarray:
        """Generate an ADSR envelope of length *n* samples."""
        sr = self.sample_rate
        a_len = int(attack * sr)
        d_len = int(decay * sr)
        r_len = int(release * sr)
        s_len = max(0, n - a_len - d_len - r_len)

        return np.concatenate([
            np.linspace(0, 1, max(1, a_len)),
            np.linspace(1, sustain, max(1, d_len)),
            np.full(s_len, sustain),
            np.linspace(sustain, 0, max(1, r_len)),
        ])[:n].astype(np.float32)

    # ------------------------------------------------------------------
    # Vocal line builder
    # ------------------------------------------------------------------

    def synthesize_vocal_line(
        self,
        syllables: List[str],
        frequencies: List[float],
        durations: List[float],
        vibrato_rate: float = 5.5,
        vibrato_depth: float = 0.02,
    ) -> np.ndarray:
        """
        Synthesize a complete vocal line from syllable/pitch/duration sequences.

        Each syllable is mapped to the first vowel found in it (case-insensitive).
        If no vowel is found, the syllable is treated as a silent rest.

        Args:
            syllables: List of syllable strings, e.g. ``["do", "re", "mi"]``
            frequencies: Fundamental frequencies (one per syllable)
            durations: Duration in seconds (one per syllable)
            vibrato_rate: Vibrato Hz
            vibrato_depth: Vibrato depth

        Returns:
            Concatenated mono audio array.
        """
        if not (len(syllables) == len(frequencies) == len(durations)):
            raise ValueError("syllables, frequencies, and durations must have the same length")

        segments: List[np.ndarray] = []
        for syllable, freq, dur in zip(syllables, frequencies, durations):
            vowel = self._extract_vowel(syllable)
            if vowel and freq > 0 and dur > 0:
                segment = self.synthesize_vowel(
                    vowel, freq, dur, vibrato_rate, vibrato_depth
                )
            else:
                # Rest
                segment = np.zeros(int(self.sample_rate * dur), dtype=np.float32)
            segments.append(segment)

        return np.concatenate(segments) if segments else np.array([], dtype=np.float32)

    @staticmethod
    def _extract_vowel(syllable: str) -> Optional[str]:
        """Return the first vowel character found in a syllable."""
        for ch in syllable.upper():
            if ch in VOWEL_FORMANTS:
                return ch
        return None

    # ------------------------------------------------------------------
    # Effects
    # ------------------------------------------------------------------

    def add_vibrato(
        self,
        audio: np.ndarray,
        rate: float = 5.5,
        depth: float = 0.003,
    ) -> np.ndarray:
        """
        Apply pitch-modulation vibrato via a fractional delay line.

        Args:
            audio: Input mono audio
            rate: Vibrato rate in Hz
            depth: Fractional delay depth in seconds

        Returns:
            Vibrato-processed audio.
        """
        n = len(audio)
        t = np.arange(n) / self.sample_rate
        delay_samples = depth * self.sample_rate * np.sin(2 * np.pi * rate * t)
        indices = np.arange(n) - delay_samples
        indices = np.clip(indices, 0, n - 1)
        i0 = indices.astype(int)
        frac = indices - i0
        i1 = np.clip(i0 + 1, 0, n - 1)
        return ((1 - frac) * audio[i0] + frac * audio[i1]).astype(np.float32)

    def add_chorus(
        self,
        audio: np.ndarray,
        voices: int = 3,
        detune_cents: float = 15.0,
        mix: float = 0.5,
    ) -> np.ndarray:
        """
        Thicken the vocal with a simple chorus (detuned copies).

        Args:
            audio: Input mono audio
            voices: Number of chorus voices
            detune_cents: Maximum pitch detune in cents
            mix: Wet/dry mix (0 = dry, 1 = full wet)

        Returns:
            Chorus-processed audio.
        """
        n = len(audio)
        chorus_sum = np.zeros(n, dtype=np.float32)

        for v in range(voices):
            rate = 0.3 + v * 0.7
            depth = (detune_cents / 1200) * 0.02
            chorus_sum += self.add_vibrato(audio, rate=rate, depth=depth)

        return (audio * (1 - mix) + (chorus_sum / voices) * mix).astype(np.float32)

    def add_breath(self, audio: np.ndarray, level: float = 0.03) -> np.ndarray:
        """Add subtle breath noise at the beginning of the phrase."""
        n = len(audio)
        breath_len = min(int(0.1 * self.sample_rate), n)
        noise = np.random.normal(0, level, breath_len).astype(np.float32)
        fade = np.linspace(1.0, 0.0, breath_len).astype(np.float32)
        result = audio.copy()
        result[:breath_len] += noise * fade
        return result

    def de_esser(self, audio: np.ndarray, threshold: float = 0.4) -> np.ndarray:
        """
        Simple de-esser: attenuate frames where the signal exceeds threshold.

        Args:
            audio: Input mono audio
            threshold: Peak threshold for gain reduction

        Returns:
            De-essed audio.
        """
        result = audio.copy()
        above = np.abs(result) > threshold
        result[above] *= threshold / (np.abs(result[above]) + 1e-9)
        return result


# ---------------------------------------------------------------------------
# Convenience helpers
# ---------------------------------------------------------------------------

def solfege_to_syllables(
    solfege: List[str],
) -> Tuple[List[str], List[str]]:
    """
    Map solfège syllables (do, re, mi, …) to phonetic syllables and vowels.

    Returns:
        ``(syllables, vowels)`` – phonetic rendering and dominant vowel.
    """
    mapping = {
        "do": ("do", "O"),
        "re": ("re", "E"),
        "mi": ("mi", "I"),
        "fa": ("fa", "A"),
        "sol": ("sol", "O"),
        "la": ("la", "A"),
        "si": ("si", "I"),
        "ti": ("ti", "I"),
    }
    syllables, vowels = [], []
    for s in solfege:
        s_lower = s.lower()
        syl, vow = mapping.get(s_lower, (s_lower, "A"))
        syllables.append(syl)
        vowels.append(vow)
    return syllables, vowels

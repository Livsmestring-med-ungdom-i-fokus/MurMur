"""
Dance Module – Dance Genre Beat & Groove Generator

Provides:
- Genre registry with BPM ranges and signature characteristics
- Drum pattern generator (kick, snare, closed hi-hat, open hi-hat, clap)
- Groove quantization / humanization
- Full beat sequence builder ready for the Live Studio
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Genre definitions
# ---------------------------------------------------------------------------

@dataclass
class DanceGenre:
    """Metadata and default settings for a dance genre."""
    name: str
    bpm_range: Tuple[int, int]          # (min, max)
    default_bpm: int
    time_signature: Tuple[int, int]     # (numerator, denominator)
    description: str
    tags: List[str] = field(default_factory=list)


DANCE_GENRES: Dict[str, DanceGenre] = {
    "house": DanceGenre(
        name="House",
        bpm_range=(120, 130),
        default_bpm=125,
        time_signature=(4, 4),
        description="Soulful 4-on-the-floor with off-beat hi-hats",
        tags=["electronic", "club", "four-on-the-floor"],
    ),
    "techno": DanceGenre(
        name="Techno",
        bpm_range=(130, 150),
        default_bpm=138,
        time_signature=(4, 4),
        description="Industrial, hypnotic, driving rhythm",
        tags=["electronic", "club", "dark"],
    ),
    "drum_and_bass": DanceGenre(
        name="Drum and Bass",
        bpm_range=(160, 180),
        default_bpm=170,
        time_signature=(4, 4),
        description="Breakbeat with heavy sub-bass",
        tags=["electronic", "breaks", "fast"],
    ),
    "hip_hop": DanceGenre(
        name="Hip-Hop",
        bpm_range=(80, 100),
        default_bpm=90,
        time_signature=(4, 4),
        description="Boom-bap or trap pocket groove",
        tags=["urban", "groove", "laid-back"],
    ),
    "trap": DanceGenre(
        name="Trap",
        bpm_range=(130, 145),
        default_bpm=140,
        time_signature=(4, 4),
        description="Hi-hat rolls, heavy 808 bass, snare on 3",
        tags=["urban", "electronic", "hi-hat-rolls"],
    ),
    "reggaeton": DanceGenre(
        name="Reggaeton",
        bpm_range=(95, 105),
        default_bpm=100,
        time_signature=(4, 4),
        description="Dembow rhythm with syncopated snare",
        tags=["latin", "dance", "dembow"],
    ),
    "afrobeats": DanceGenre(
        name="Afrobeats",
        bpm_range=(100, 115),
        default_bpm=108,
        time_signature=(4, 4),
        description="Polyrhythmic West-African groove",
        tags=["african", "dance", "groove"],
    ),
    "pop": DanceGenre(
        name="Pop",
        bpm_range=(100, 128),
        default_bpm=120,
        time_signature=(4, 4),
        description="Clean, accessible 4/4 pop beat",
        tags=["mainstream", "upbeat"],
    ),
}

# Drum voice names used throughout the module
DRUM_VOICES = ["kick", "snare", "hihat_closed", "hihat_open", "clap"]

# ---------------------------------------------------------------------------
# Step-sequencer patterns  (1 bar = 16 sixteenth-note steps)
# ---------------------------------------------------------------------------

# Each pattern is a list of 16 booleans (True = hit on that step)
PATTERNS: Dict[str, Dict[str, List[bool]]] = {
    "house": {
        "kick":         [1,0,0,0, 1,0,0,0, 1,0,0,0, 1,0,0,0],
        "snare":        [0,0,0,0, 1,0,0,0, 0,0,0,0, 1,0,0,0],
        "hihat_closed": [0,0,1,0, 0,0,1,0, 0,0,1,0, 0,0,1,0],
        "hihat_open":   [0,0,0,0, 0,0,0,1, 0,0,0,0, 0,0,0,1],
        "clap":         [0,0,0,0, 1,0,0,0, 0,0,0,0, 1,0,0,0],
    },
    "techno": {
        "kick":         [1,0,0,0, 1,0,0,0, 1,0,0,0, 1,0,0,0],
        "snare":        [0,0,0,0, 0,0,0,0, 0,0,0,0, 1,0,0,0],
        "hihat_closed": [1,0,1,0, 1,0,1,0, 1,0,1,0, 1,0,1,0],
        "hihat_open":   [0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0],
        "clap":         [0,0,0,0, 1,0,0,0, 0,0,0,0, 1,0,0,0],
    },
    "drum_and_bass": {
        "kick":         [1,0,0,0, 0,0,0,0, 0,0,1,0, 0,0,0,0],
        "snare":        [0,0,0,0, 1,0,0,0, 0,0,0,0, 1,0,0,1],
        "hihat_closed": [1,1,1,1, 1,1,1,1, 1,1,1,1, 1,1,1,1],
        "hihat_open":   [0,0,0,0, 0,1,0,0, 0,0,0,0, 0,1,0,0],
        "clap":         [0,0,0,0, 1,0,0,0, 0,0,0,0, 1,0,0,0],
    },
    "hip_hop": {
        "kick":         [1,0,0,1, 0,0,1,0, 0,1,0,0, 1,0,0,0],
        "snare":        [0,0,0,0, 1,0,0,0, 0,0,0,0, 1,0,0,0],
        "hihat_closed": [1,0,1,0, 1,0,1,0, 1,0,1,0, 1,0,1,0],
        "hihat_open":   [0,0,0,0, 0,0,0,1, 0,0,0,0, 0,0,0,1],
        "clap":         [0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0],
    },
    "trap": {
        "kick":         [1,0,0,0, 0,0,0,0, 1,0,0,0, 0,0,0,0],
        "snare":        [0,0,0,0, 0,0,0,0, 1,0,0,0, 0,0,0,0],
        "hihat_closed": [1,1,1,1, 1,1,1,1, 1,1,1,1, 1,1,1,1],
        "hihat_open":   [0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,1],
        "clap":         [0,0,0,0, 1,0,0,0, 0,0,0,0, 1,0,0,0],
    },
    "reggaeton": {
        "kick":         [1,0,0,0, 1,0,0,0, 0,0,0,0, 1,0,0,0],
        "snare":        [0,0,1,0, 0,0,1,0, 0,0,1,0, 0,0,1,0],
        "hihat_closed": [1,0,1,0, 1,0,1,0, 1,0,1,0, 1,0,1,0],
        "hihat_open":   [0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0],
        "clap":         [0,0,0,0, 0,0,1,0, 0,0,0,0, 0,0,1,0],
    },
    "afrobeats": {
        "kick":         [1,0,0,1, 0,0,1,0, 1,0,0,1, 0,0,1,0],
        "snare":        [0,0,1,0, 1,0,0,0, 0,0,1,0, 1,0,0,0],
        "hihat_closed": [1,1,0,1, 1,1,0,1, 1,1,0,1, 1,1,0,1],
        "hihat_open":   [0,0,0,0, 0,0,0,1, 0,0,0,0, 0,0,0,1],
        "clap":         [0,0,0,0, 1,0,0,0, 0,0,0,0, 1,0,0,0],
    },
    "pop": {
        "kick":         [1,0,0,0, 1,0,0,0, 1,0,0,0, 1,0,0,0],
        "snare":        [0,0,0,0, 1,0,0,0, 0,0,0,0, 1,0,0,0],
        "hihat_closed": [1,0,1,0, 1,0,1,0, 1,0,1,0, 1,0,1,0],
        "hihat_open":   [0,0,0,0, 0,0,0,1, 0,0,0,0, 0,0,0,1],
        "clap":         [0,0,0,0, 1,0,0,0, 0,0,0,0, 1,0,0,0],
    },
}


# ---------------------------------------------------------------------------
# Drum synthesizer (simple, parameter-based)
# ---------------------------------------------------------------------------

class DrumSynthesizer:
    """Synthesize individual drum hits with basic signal modelling."""

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate

    def _t(self, duration: float) -> np.ndarray:
        return np.arange(int(self.sample_rate * duration)) / self.sample_rate

    def kick(self, duration: float = 0.5, pitch: float = 60.0, punch: float = 200.0) -> np.ndarray:
        """Synthesize a kick drum (pitch-swept sine + noise transient)."""
        t = self._t(duration)
        # Pitch sweep from `punch` Hz down to `pitch` Hz
        env_pitch = np.exp(-12 * t)
        freq = pitch + (punch - pitch) * env_pitch
        phase = np.cumsum(2 * np.pi * freq / self.sample_rate)
        tone = np.sin(phase)

        # Noise transient
        noise = np.random.normal(0, 0.3, len(t))
        noise_env = np.exp(-50 * t)

        amp_env = np.exp(-8 * t)
        signal = (tone + noise * noise_env) * amp_env
        return self._normalize(signal, 0.85)

    def snare(self, duration: float = 0.2, noise_level: float = 0.7) -> np.ndarray:
        """Synthesize a snare drum (tone body + white noise)."""
        t = self._t(duration)
        tone = np.sin(2 * np.pi * 200 * t) * np.exp(-20 * t)
        noise = np.random.normal(0, noise_level, len(t)) * np.exp(-15 * t)
        signal = tone + noise
        return self._normalize(signal, 0.75)

    def hihat_closed(self, duration: float = 0.05) -> np.ndarray:
        """Closed hi-hat – short filtered noise burst."""
        t = self._t(duration)
        noise = np.random.normal(0, 1.0, len(t))
        env = np.exp(-60 * t)
        # Simple high-pass: subtract low-freq content
        smoothed = np.convolve(noise, np.ones(4) / 4, mode="same")
        signal = (noise - smoothed) * env
        return self._normalize(signal, 0.5)

    def hihat_open(self, duration: float = 0.3) -> np.ndarray:
        """Open hi-hat – longer filtered noise with slower decay."""
        t = self._t(duration)
        noise = np.random.normal(0, 1.0, len(t))
        env = np.exp(-8 * t)
        smoothed = np.convolve(noise, np.ones(4) / 4, mode="same")
        signal = (noise - smoothed) * env
        return self._normalize(signal, 0.55)

    def clap(self, duration: float = 0.15) -> np.ndarray:
        """Clap – burst of noise with characteristic envelope."""
        t = self._t(duration)
        noise = np.random.normal(0, 1.0, len(t))
        # Multi-peak envelope simulating hand clap
        env = (
            np.exp(-50 * t)
            + 0.5 * np.exp(-50 * np.maximum(t - 0.01, 0))
            + 0.3 * np.exp(-50 * np.maximum(t - 0.02, 0))
        )
        signal = noise * env
        return self._normalize(signal, 0.65)

    @staticmethod
    def _normalize(signal: np.ndarray, target: float = 0.8) -> np.ndarray:
        peak = np.max(np.abs(signal) + 1e-9)
        return (signal * target / peak).astype(np.float32)

    def hit(self, voice: str) -> np.ndarray:
        """Dispatch to the correct synthesizer by voice name."""
        dispatch = {
            "kick": self.kick,
            "snare": self.snare,
            "hihat_closed": self.hihat_closed,
            "hihat_open": self.hihat_open,
            "clap": self.clap,
        }
        if voice not in dispatch:
            raise ValueError(f"Unknown drum voice '{voice}'. Use one of {DRUM_VOICES}")
        return dispatch[voice]()


# ---------------------------------------------------------------------------
# Beat generator
# ---------------------------------------------------------------------------

class BeatGenerator:
    """
    High-level beat generator that converts a step-sequencer pattern into
    audio tracks ready for the Live Studio.
    """

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.drum_synth = DrumSynthesizer(sample_rate)

    def generate_bar(
        self,
        genre: str = "house",
        bpm: Optional[int] = None,
        bars: int = 1,
        humanize: float = 0.0,
    ) -> Dict[str, np.ndarray]:
        """
        Generate one or more bars of drums for the requested genre.

        Args:
            genre: One of the keys in ``DANCE_GENRES``
            bpm: Override BPM (uses genre default if None)
            bars: Number of bars to generate
            humanize: Amount of timing randomness (0 = grid, 1 = very loose)

        Returns:
            Dict mapping drum voice → audio array (one track per voice).
        """
        if genre not in DANCE_GENRES:
            raise ValueError(f"Unknown genre '{genre}'. Available: {list(DANCE_GENRES)}")

        genre_info = DANCE_GENRES[genre]
        actual_bpm = bpm if bpm is not None else genre_info.default_bpm

        beat_pattern = PATTERNS.get(genre, PATTERNS["pop"])
        step_duration = 60 / actual_bpm / 4  # sixteenth note duration

        tracks: Dict[str, np.ndarray] = {}

        for voice in DRUM_VOICES:
            hit_audio = self.drum_synth.hit(voice)
            pattern = beat_pattern.get(voice, [0] * 16)
            bar_audio = self._render_pattern(
                pattern, hit_audio, step_duration, bars, humanize
            )
            tracks[voice] = bar_audio

        return tracks

    def _render_pattern(
        self,
        pattern: List[bool],
        hit_audio: np.ndarray,
        step_duration: float,
        bars: int,
        humanize: float,
    ) -> np.ndarray:
        """Render a single voice pattern into an audio buffer."""
        steps = len(pattern)
        bar_samples = int(steps * step_duration * self.sample_rate)
        total_samples = bar_samples * bars
        buffer = np.zeros(total_samples, dtype=np.float32)
        hit_len = len(hit_audio)

        for bar_idx in range(bars):
            for step_idx, active in enumerate(pattern):
                if not active:
                    continue
                base_pos = (bar_idx * steps + step_idx) * int(
                    step_duration * self.sample_rate
                )
                # Humanize: random early/late offset
                jitter = 0
                if humanize > 0:
                    max_jitter = int(humanize * 0.02 * self.sample_rate)
                    jitter = int(np.random.uniform(-max_jitter, max_jitter))

                pos = max(0, base_pos + jitter)
                end = min(total_samples, pos + hit_len)
                buffer[pos:end] += hit_audio[: end - pos]

        # Soft-clip to prevent clipping artifacts
        return np.tanh(buffer).astype(np.float32)

    def get_genre_info(self, genre: str) -> DanceGenre:
        """Return metadata for a dance genre."""
        if genre not in DANCE_GENRES:
            raise ValueError(f"Unknown genre '{genre}'")
        return DANCE_GENRES[genre]


# ---------------------------------------------------------------------------
# Convenience helpers
# ---------------------------------------------------------------------------

def list_genres() -> List[str]:
    """Return all available dance genre names."""
    return sorted(DANCE_GENRES.keys())


def genre_description(genre: str) -> str:
    """Return a human-readable description for a genre."""
    info = DANCE_GENRES.get(genre)
    if info is None:
        return f"Unknown genre '{genre}'"
    return (
        f"{info.name} | BPM: {info.bpm_range[0]}–{info.bpm_range[1]} "
        f"(default {info.default_bpm}) | {info.description}"
    )

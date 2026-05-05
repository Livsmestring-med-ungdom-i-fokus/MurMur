"""
Artist Mode Module – Advanced Composition & Arrangement Tools

Provides:
- Song section builder (intro, verse, pre-chorus, chorus, bridge, outro)
- Style presets for popular genres (pop, jazz, EDM, classical, …)
- Multi-section arrangement planner
- Inspiration engine for creative direction
- Performance variations (fills, runs, dynamics)
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Section definitions
# ---------------------------------------------------------------------------

SECTION_TYPES = [
    "intro",
    "verse",
    "pre_chorus",
    "chorus",
    "bridge",
    "drop",
    "breakdown",
    "outro",
    "interlude",
    "solo",
]


@dataclass
class Section:
    """A single section of a song arrangement."""
    section_type: str
    bars: int                      # Length in bars
    key: str = "C"
    scale: str = "major"
    bpm: int = 120
    intensity: float = 0.5        # 0.0 (soft) → 1.0 (full energy)
    notes: str = ""               # Optional melody/chord notes description
    tags: List[str] = field(default_factory=list)

    def summary(self) -> str:
        return (
            f"[{self.section_type.upper()}] {self.bars} bars | "
            f"{self.key} {self.scale} | {self.bpm} BPM | "
            f"intensity={self.intensity:.1f}"
        )


# ---------------------------------------------------------------------------
# Style presets
# ---------------------------------------------------------------------------

@dataclass
class StylePreset:
    """A genre style preset that populates sensible section defaults."""
    name: str
    default_bpm: int
    default_key: str
    default_scale: str
    section_order: List[str]
    section_bars: Dict[str, int]
    section_intensity: Dict[str, float]
    description: str
    production_tips: List[str] = field(default_factory=list)


STYLE_PRESETS: Dict[str, StylePreset] = {
    "pop": StylePreset(
        name="Pop",
        default_bpm=120,
        default_key="C",
        default_scale="major",
        section_order=["intro", "verse", "pre_chorus", "chorus",
                        "verse", "pre_chorus", "chorus", "bridge",
                        "chorus", "outro"],
        section_bars={
            "intro": 4, "verse": 8, "pre_chorus": 4,
            "chorus": 8, "bridge": 4, "outro": 4,
        },
        section_intensity={
            "intro": 0.3, "verse": 0.5, "pre_chorus": 0.65,
            "chorus": 0.9, "bridge": 0.6, "outro": 0.2,
        },
        description="Verse-chorus pop song structure",
        production_tips=[
            "Use four-on-the-floor kick pattern in choruses",
            "Layer light pads under verses for warmth",
            "Add an octave bass-drop at the chorus downbeat",
        ],
    ),
    "edm": StylePreset(
        name="EDM",
        default_bpm=128,
        default_key="A",
        default_scale="minor",
        section_order=["intro", "verse", "pre_chorus", "drop",
                        "breakdown", "verse", "pre_chorus", "drop", "outro"],
        section_bars={
            "intro": 8, "verse": 8, "pre_chorus": 4,
            "drop": 16, "breakdown": 8, "outro": 8,
        },
        section_intensity={
            "intro": 0.2, "verse": 0.55, "pre_chorus": 0.75,
            "drop": 1.0, "breakdown": 0.15, "outro": 0.3,
        },
        description="Build-drop-breakdown EDM structure",
        production_tips=[
            "Use a white-noise sweep into the drop",
            "High-pass filter bass in breakdown for tension",
            "Sidechain compression kick into pads for pumping effect",
        ],
    ),
    "jazz": StylePreset(
        name="Jazz",
        default_bpm=130,
        default_key="F",
        default_scale="major",
        section_order=["intro", "verse", "chorus", "solo", "verse", "chorus", "outro"],
        section_bars={
            "intro": 4, "verse": 16, "chorus": 8, "solo": 16, "outro": 4,
        },
        section_intensity={
            "intro": 0.3, "verse": 0.5, "chorus": 0.7, "solo": 0.8, "outro": 0.4,
        },
        description="AABA jazz-standard form with solo section",
        production_tips=[
            "Swing your eighth notes at ~60% long / 40% short",
            "Add 7th and 9th chord extensions throughout",
            "Use call-and-response between melody and comping",
        ],
    ),
    "hip_hop": StylePreset(
        name="Hip-Hop",
        default_bpm=90,
        default_key="D",
        default_scale="minor",
        section_order=["intro", "verse", "chorus", "verse", "chorus",
                        "bridge", "chorus", "outro"],
        section_bars={
            "intro": 4, "verse": 16, "chorus": 8, "bridge": 8, "outro": 4,
        },
        section_intensity={
            "intro": 0.25, "verse": 0.6, "chorus": 0.85,
            "bridge": 0.55, "outro": 0.2,
        },
        description="Classic hip-hop verse-hook format",
        production_tips=[
            "Sample-chop or replay melodic loops as the foundation",
            "Keep 808 bass and kick occupying the same frequency space",
            "Use vocal ad-libs and doubles in the hook",
        ],
    ),
    "classical": StylePreset(
        name="Classical",
        default_bpm=100,
        default_key="G",
        default_scale="major",
        section_order=["intro", "verse", "bridge", "verse", "chorus", "outro"],
        section_bars={
            "intro": 8, "verse": 16, "bridge": 8, "chorus": 16, "outro": 8,
        },
        section_intensity={
            "intro": 0.4, "verse": 0.6, "bridge": 0.8,
            "chorus": 0.9, "outro": 0.3,
        },
        description="Sonata-like ABA' classical form",
        production_tips=[
            "Use long dynamic hairpins (crescendo/decrescendo)",
            "Develop motifs through variation and inversion",
            "Balance foreground melody with counterpoint in inner voices",
        ],
    ),
    "reggae": StylePreset(
        name="Reggae",
        default_bpm=80,
        default_key="E",
        default_scale="minor",
        section_order=["intro", "verse", "chorus", "verse", "chorus", "bridge", "outro"],
        section_bars={
            "intro": 4, "verse": 8, "chorus": 8, "bridge": 4, "outro": 4,
        },
        section_intensity={
            "intro": 0.25, "verse": 0.55, "chorus": 0.75,
            "bridge": 0.6, "outro": 0.2,
        },
        description="Laid-back one-drop reggae groove",
        production_tips=[
            "Skank rhythm guitar on the off-beat (2 and 4)",
            "Heavy reverb on snare and vocals",
            "Emphasise the bass melody – it carries the harmony",
        ],
    ),
}


# ---------------------------------------------------------------------------
# Arrangement planner
# ---------------------------------------------------------------------------

class Arrangement:
    """A complete song arrangement composed of ordered sections."""

    def __init__(self, title: str = "Untitled"):
        self.title = title
        self.sections: List[Section] = []

    def add_section(self, section: Section) -> "Arrangement":
        """Append a section to the arrangement."""
        self.sections.append(section)
        return self

    def total_bars(self) -> int:
        """Total number of bars in the arrangement."""
        return sum(s.bars for s in self.sections)

    def estimated_duration(self, bpm: Optional[int] = None) -> float:
        """Estimated duration in seconds."""
        seconds = 0.0
        for section in self.sections:
            actual_bpm = bpm or section.bpm
            seconds += section.bars * (4 * 60 / actual_bpm)
        return seconds

    def summary(self) -> str:
        """Return a multi-line human-readable arrangement summary."""
        lines = [
            f"🎵 Arrangement: {self.title}",
            f"   Total bars: {self.total_bars()}",
            f"   Est. duration: {self.estimated_duration():.1f}s",
            "",
        ]
        for idx, section in enumerate(self.sections, start=1):
            lines.append(f"  {idx:2}. {section.summary()}")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        """Serialise the arrangement to a plain dictionary."""
        return {
            "title": self.title,
            "sections": [
                {
                    "type": s.section_type,
                    "bars": s.bars,
                    "key": s.key,
                    "scale": s.scale,
                    "bpm": s.bpm,
                    "intensity": s.intensity,
                    "notes": s.notes,
                    "tags": s.tags,
                }
                for s in self.sections
            ],
            "total_bars": self.total_bars(),
            "estimated_duration_seconds": self.estimated_duration(),
        }


class ArtistMode:
    """
    Artist Mode – high-level composition assistant.

    Combines style presets, arrangement planning, and an inspiration engine
    to help artists build complete songs quickly.
    """

    def __init__(self, default_style: str = "pop"):
        if default_style not in STYLE_PRESETS:
            raise ValueError(
                f"Unknown style '{default_style}'. Available: {list(STYLE_PRESETS)}"
            )
        self.default_style = default_style
        self.preset: StylePreset = STYLE_PRESETS[default_style]
        self._inspiration_seed: Optional[int] = None

    # ------------------------------------------------------------------
    # Arrangement building
    # ------------------------------------------------------------------

    def build_arrangement(
        self,
        title: str = "Untitled",
        style: Optional[str] = None,
        key: Optional[str] = None,
        bpm: Optional[int] = None,
        custom_order: Optional[List[str]] = None,
    ) -> Arrangement:
        """
        Build a complete arrangement from a style preset.

        Args:
            title: Song title
            style: Style preset name (overrides the instance default)
            key: Override the preset's default key
            bpm: Override the preset's default BPM
            custom_order: Optional list of section type names overriding the
                          preset's default section order.

        Returns:
            A fully populated :class:`Arrangement`.
        """
        preset = STYLE_PRESETS.get(style or self.default_style, self.preset)
        actual_bpm = bpm or preset.default_bpm
        actual_key = key or preset.default_key
        order = custom_order or preset.section_order

        arrangement = Arrangement(title=title)
        for section_type in order:
            bars = preset.section_bars.get(section_type, 8)
            intensity = preset.section_intensity.get(section_type, 0.5)
            arrangement.add_section(
                Section(
                    section_type=section_type,
                    bars=bars,
                    key=actual_key,
                    scale=preset.default_scale,
                    bpm=actual_bpm,
                    intensity=intensity,
                )
            )

        return arrangement

    def create_section(
        self,
        section_type: str,
        key: str = "C",
        scale: str = "major",
        bpm: int = 120,
        bars: int = 8,
        intensity: float = 0.5,
    ) -> Section:
        """Create a single named section with the given parameters."""
        if section_type not in SECTION_TYPES:
            raise ValueError(
                f"Unknown section type '{section_type}'. "
                f"Use one of: {SECTION_TYPES}"
            )
        return Section(
            section_type=section_type,
            bars=bars,
            key=key,
            scale=scale,
            bpm=bpm,
            intensity=intensity,
        )

    # ------------------------------------------------------------------
    # Style & preset helpers
    # ------------------------------------------------------------------

    def set_style(self, style: str) -> None:
        """Switch the active style preset."""
        if style not in STYLE_PRESETS:
            raise ValueError(f"Unknown style '{style}'")
        self.default_style = style
        self.preset = STYLE_PRESETS[style]

    def get_production_tips(self, style: Optional[str] = None) -> List[str]:
        """Return production tips for the current (or specified) style."""
        preset = STYLE_PRESETS.get(style or self.default_style, self.preset)
        return list(preset.production_tips)

    # ------------------------------------------------------------------
    # Inspiration engine
    # ------------------------------------------------------------------

    def get_inspiration(self, seed: Optional[int] = None) -> Dict[str, str]:
        """
        Generate a random creative inspiration prompt.

        Args:
            seed: Optional random seed for reproducibility.

        Returns:
            A dict with ``theme``, ``mood``, ``texture``, and ``tip`` keys.
        """
        rng = random.Random(seed if seed is not None else self._inspiration_seed)

        themes = [
            "Longing for home", "First light of dawn", "Urban solitude",
            "Joy after rain", "A conversation between strangers",
            "The feeling of weightlessness", "Nostalgia for the future",
            "Dancing in an empty room", "The edge of a forest at midnight",
        ]
        moods = [
            "melancholic", "euphoric", "tense", "playful", "dreamy",
            "triumphant", "introspective", "restless", "serene",
        ]
        textures = [
            "sparse and minimalist", "dense and layered", "warm and organic",
            "cold and metallic", "rhythmically complex", "melodically simple",
            "heavily processed", "lush and reverberant", "dry and punchy",
        ]
        tips = [
            "Start with the most unusual element and build around it",
            "Strip the arrangement to a single instrument for the bridge",
            "Borrow a chord from the parallel minor key",
            "Flip the verse and chorus dynamics",
            "Use silence as a musical element",
            "Write the melody first, then derive the chords",
            "Record a real-world sound and use it as a rhythmic element",
        ]

        return {
            "theme":   rng.choice(themes),
            "mood":    rng.choice(moods),
            "texture": rng.choice(textures),
            "tip":     rng.choice(tips),
        }

    def generate_fill(self, style: Optional[str] = None, bars: int = 1) -> Section:
        """Generate a short fill / transition section."""
        preset = STYLE_PRESETS.get(style or self.default_style, self.preset)
        return Section(
            section_type="interlude",
            bars=bars,
            key=preset.default_key,
            scale=preset.default_scale,
            bpm=preset.default_bpm,
            intensity=0.9,
            tags=["fill", "transition"],
        )


# ---------------------------------------------------------------------------
# Convenience helpers
# ---------------------------------------------------------------------------

def list_styles() -> List[str]:
    """Return all available style preset names."""
    return sorted(STYLE_PRESETS.keys())


def list_section_types() -> List[str]:
    """Return all recognised section type names."""
    return SECTION_TYPES[:]

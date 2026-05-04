"""Tests for music_ai_core.artist_mode – sections, arrangements, and ArtistMode."""

import pytest

from music_ai_core.artist_mode import (
    SECTION_TYPES,
    STYLE_PRESETS,
    Section,
    Arrangement,
    ArtistMode,
    list_styles,
    list_section_types,
)


# ---------------------------------------------------------------------------
# Section
# ---------------------------------------------------------------------------

class TestSection:
    def test_defaults(self):
        s = Section(section_type="verse", bars=8)
        assert s.key == "C"
        assert s.scale == "major"
        assert s.bpm == 120
        assert s.intensity == 0.5

    def test_summary_contains_type(self):
        s = Section(section_type="chorus", bars=4)
        assert "CHORUS" in s.summary()

    def test_summary_contains_bars(self):
        s = Section(section_type="verse", bars=16)
        assert "16" in s.summary()

    def test_custom_values(self):
        s = Section(section_type="bridge", bars=4, key="G", bpm=90, intensity=0.8)
        assert s.key == "G"
        assert s.bpm == 90
        assert s.intensity == 0.8


# ---------------------------------------------------------------------------
# Arrangement
# ---------------------------------------------------------------------------

class TestArrangement:
    def test_empty_arrangement(self):
        arr = Arrangement("Test Song")
        assert arr.total_bars() == 0
        assert arr.estimated_duration() == pytest.approx(0.0)

    def test_add_section_returns_self(self):
        arr = Arrangement()
        result = arr.add_section(Section(section_type="verse", bars=8))
        assert result is arr

    def test_total_bars(self):
        arr = Arrangement()
        arr.add_section(Section(section_type="verse", bars=8))
        arr.add_section(Section(section_type="chorus", bars=4))
        assert arr.total_bars() == 12

    def test_estimated_duration(self):
        arr = Arrangement()
        # 4 bars at 120 BPM: 4 bars * 4 beats/bar * (60/120) s/beat = 8 s
        arr.add_section(Section(section_type="verse", bars=4, bpm=120))
        assert arr.estimated_duration() == pytest.approx(8.0, rel=1e-6)

    def test_estimated_duration_bpm_override(self):
        arr = Arrangement()
        arr.add_section(Section(section_type="verse", bars=4, bpm=60))
        # At 60 BPM override of 120: same bars run at 120 BPM -> half the time
        dur_slow = arr.estimated_duration()
        dur_fast = arr.estimated_duration(bpm=120)
        assert dur_slow == pytest.approx(dur_fast * 2, rel=1e-6)

    def test_summary_contains_title(self):
        arr = Arrangement(title="My Song")
        assert "My Song" in arr.summary()

    def test_to_dict_structure(self):
        arr = Arrangement(title="Test")
        arr.add_section(Section(section_type="intro", bars=4, key="A", bpm=100))
        d = arr.to_dict()
        assert d["title"] == "Test"
        assert d["total_bars"] == 4
        assert len(d["sections"]) == 1
        assert d["sections"][0]["type"] == "intro"


# ---------------------------------------------------------------------------
# STYLE_PRESETS
# ---------------------------------------------------------------------------

class TestStylePresets:
    def test_known_styles_exist(self):
        for style in ("pop", "edm", "jazz", "hip_hop", "classical", "reggae"):
            assert style in STYLE_PRESETS

    def test_preset_has_section_order(self):
        for name, preset in STYLE_PRESETS.items():
            assert len(preset.section_order) > 0, f"{name} section_order is empty"

    def test_preset_bpm_positive(self):
        for name, preset in STYLE_PRESETS.items():
            assert preset.default_bpm > 0


# ---------------------------------------------------------------------------
# ArtistMode
# ---------------------------------------------------------------------------

class TestArtistMode:
    def test_default_style_pop(self):
        am = ArtistMode("pop")
        assert am.default_style == "pop"

    def test_invalid_style_raises(self):
        with pytest.raises(ValueError, match="Unknown style"):
            ArtistMode("bluegrass")

    def test_build_arrangement_returns_arrangement(self):
        am = ArtistMode("pop")
        arr = am.build_arrangement(title="My Pop Song")
        assert isinstance(arr, Arrangement)
        assert arr.title == "My Pop Song"

    def test_build_arrangement_has_sections(self):
        am = ArtistMode("edm")
        arr = am.build_arrangement()
        assert len(arr.sections) > 0

    def test_build_arrangement_bpm_override(self):
        am = ArtistMode("pop")
        arr = am.build_arrangement(bpm=90)
        for section in arr.sections:
            assert section.bpm == 90

    def test_build_arrangement_key_override(self):
        am = ArtistMode("jazz")
        arr = am.build_arrangement(key="Bb")
        for section in arr.sections:
            assert section.key == "Bb"  # note: key is stored as provided

    def test_build_arrangement_custom_order(self):
        am = ArtistMode("pop")
        arr = am.build_arrangement(custom_order=["intro", "outro"])
        assert len(arr.sections) == 2

    def test_create_section_valid(self):
        am = ArtistMode("pop")
        section = am.create_section("chorus", key="G", bpm=130, bars=8)
        assert section.section_type == "chorus"
        assert section.bpm == 130

    def test_create_section_invalid_type_raises(self):
        am = ArtistMode("pop")
        with pytest.raises(ValueError, match="Unknown section type"):
            am.create_section("refrain")

    def test_set_style(self):
        am = ArtistMode("pop")
        am.set_style("jazz")
        assert am.default_style == "jazz"

    def test_set_style_invalid_raises(self):
        am = ArtistMode("pop")
        with pytest.raises(ValueError, match="Unknown style"):
            am.set_style("disco")

    def test_get_production_tips_non_empty(self):
        am = ArtistMode("pop")
        tips = am.get_production_tips()
        assert len(tips) > 0
        assert all(isinstance(t, str) for t in tips)

    def test_get_inspiration_has_keys(self):
        am = ArtistMode("pop")
        insp = am.get_inspiration(seed=42)
        for key in ("theme", "mood", "texture", "tip"):
            assert key in insp

    def test_get_inspiration_reproducible_with_seed(self):
        am = ArtistMode("pop")
        a = am.get_inspiration(seed=7)
        b = am.get_inspiration(seed=7)
        assert a == b

    def test_generate_fill_returns_section(self):
        am = ArtistMode("pop")
        fill = am.generate_fill(bars=2)
        assert isinstance(fill, Section)
        assert fill.bars == 2
        assert "fill" in fill.tags


# ---------------------------------------------------------------------------
# Convenience helpers
# ---------------------------------------------------------------------------

class TestArtistModeHelpers:
    def test_list_styles_sorted(self):
        styles = list_styles()
        assert styles == sorted(styles)
        assert "pop" in styles

    def test_list_section_types_non_empty(self):
        types = list_section_types()
        assert "verse" in types
        assert "chorus" in types

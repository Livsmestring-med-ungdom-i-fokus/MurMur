"""Tests for music_ai_core.artist_mode — arrangement and composition tools."""

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


class TestSection:
    def test_section_summary_contains_type(self):
        section = Section(section_type="verse", bars=8, key="C", scale="major", bpm=120)
        assert "VERSE" in section.summary()

    def test_section_summary_contains_bars(self):
        section = Section(section_type="chorus", bars=4)
        assert "4" in section.summary()

    def test_section_default_intensity(self):
        section = Section(section_type="intro", bars=4)
        assert 0.0 <= section.intensity <= 1.0


class TestArrangement:
    def setup_method(self):
        self.arr = Arrangement(title="Test Song")

    def test_empty_arrangement_has_zero_bars(self):
        assert self.arr.total_bars() == 0

    def test_add_section_returns_arrangement(self):
        result = self.arr.add_section(Section("verse", bars=8))
        assert result is self.arr

    def test_total_bars_sums_sections(self):
        self.arr.add_section(Section("verse", bars=8))
        self.arr.add_section(Section("chorus", bars=4))
        assert self.arr.total_bars() == 12

    def test_estimated_duration_positive(self):
        self.arr.add_section(Section("verse", bars=8, bpm=120))
        duration = self.arr.estimated_duration()
        assert duration > 0

    def test_estimated_duration_at_120bpm(self):
        # 1 bar at 120 BPM = 4 beats × 0.5s = 2.0 seconds
        self.arr.add_section(Section("verse", bars=1, bpm=120))
        assert self.arr.estimated_duration() == pytest.approx(2.0, rel=1e-4)

    def test_summary_contains_title(self):
        summary = self.arr.summary()
        assert "Test Song" in summary

    def test_to_dict_structure(self):
        self.arr.add_section(Section("intro", bars=4, key="G", scale="minor", bpm=90))
        d = self.arr.to_dict()
        assert d["title"] == "Test Song"
        assert len(d["sections"]) == 1
        assert d["sections"][0]["type"] == "intro"
        assert d["total_bars"] == 4


class TestArtistMode:
    def test_default_style_is_pop(self):
        artist = ArtistMode()
        assert artist.default_style == "pop"

    def test_unknown_style_raises(self):
        with pytest.raises(ValueError, match="Unknown style"):
            ArtistMode(default_style="country")

    def test_build_arrangement_returns_arrangement(self):
        artist = ArtistMode("pop")
        arr = artist.build_arrangement(title="My Song")
        assert isinstance(arr, Arrangement)

    def test_build_arrangement_has_sections(self):
        artist = ArtistMode("edm")
        arr = artist.build_arrangement()
        assert len(arr.sections) > 0

    def test_build_arrangement_with_custom_key_and_bpm(self):
        artist = ArtistMode("jazz")
        arr = artist.build_arrangement(key="D", bpm=140)
        for section in arr.sections:
            assert section.key == "D"
            assert section.bpm == 140

    def test_build_arrangement_custom_order(self):
        artist = ArtistMode("pop")
        arr = artist.build_arrangement(custom_order=["intro", "chorus", "outro"])
        types = [s.section_type for s in arr.sections]
        assert types == ["intro", "chorus", "outro"]

    def test_create_section_valid_type(self):
        artist = ArtistMode()
        section = artist.create_section("verse", key="A", bpm=100)
        assert section.section_type == "verse"
        assert section.key == "A"
        assert section.bpm == 100

    def test_create_section_invalid_type_raises(self):
        artist = ArtistMode()
        with pytest.raises(ValueError, match="Unknown section type"):
            artist.create_section("refrain")

    def test_set_style_changes_preset(self):
        artist = ArtistMode("pop")
        artist.set_style("jazz")
        assert artist.default_style == "jazz"

    def test_set_style_invalid_raises(self):
        artist = ArtistMode()
        with pytest.raises(ValueError, match="Unknown style"):
            artist.set_style("ragtime")

    def test_get_production_tips_returns_list(self):
        artist = ArtistMode("edm")
        tips = artist.get_production_tips()
        assert isinstance(tips, list)
        assert len(tips) > 0

    def test_get_production_tips_for_style(self):
        artist = ArtistMode()
        tips = artist.get_production_tips("jazz")
        assert isinstance(tips, list)

    def test_get_inspiration_returns_dict(self):
        artist = ArtistMode()
        inspiration = artist.get_inspiration(seed=42)
        assert set(inspiration.keys()) == {"theme", "mood", "texture", "tip"}

    def test_get_inspiration_deterministic_with_seed(self):
        artist = ArtistMode()
        first = artist.get_inspiration(seed=7)
        second = artist.get_inspiration(seed=7)
        assert first == second

    def test_get_inspiration_different_seeds_differ(self):
        artist = ArtistMode()
        a = artist.get_inspiration(seed=1)
        b = artist.get_inspiration(seed=99)
        # Not guaranteed to differ, but extremely likely
        assert a != b

    def test_generate_fill_returns_section(self):
        artist = ArtistMode("pop")
        fill = artist.generate_fill(bars=2)
        assert isinstance(fill, Section)
        assert fill.bars == 2
        assert "fill" in fill.tags

    def test_all_styles_build_arrangement(self):
        for style in STYLE_PRESETS:
            artist = ArtistMode(style)
            arr = artist.build_arrangement()
            assert len(arr.sections) > 0


class TestListHelpers:
    def test_list_styles_sorted(self):
        styles = list_styles()
        assert styles == sorted(styles)
        assert len(styles) > 0

    def test_list_section_types_contains_expected(self):
        types = list_section_types()
        for expected in ["verse", "chorus", "bridge", "outro"]:
            assert expected in types

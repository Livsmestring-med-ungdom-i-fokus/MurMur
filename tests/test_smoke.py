"""
Smoke tests for the Music AI Core system.

Verifies that core modules can be imported and instantiated without errors.
"""


def test_elements_import():
    """Test that the elements module imports cleanly."""
    from music_ai_core.elements import (
        NOTE_FREQUENCIES,
        ALL_NOTE_NAMES,
        SCALE_PATTERNS,
        list_scales,
        list_chords,
        list_rhythms,
    )
    assert len(NOTE_FREQUENCIES) > 0
    assert len(ALL_NOTE_NAMES) == 12
    assert "major" in SCALE_PATTERNS
    assert len(list_scales()) > 0
    assert len(list_chords()) > 0
    assert len(list_rhythms()) > 0


def test_get_scale():
    """Test scale generation."""
    from music_ai_core.elements import get_scale
    notes = get_scale("C", "major", octave=4)
    assert len(notes) == 7
    # Each note is a (name, frequency) tuple
    assert notes[0][0] == "C4"
    assert isinstance(notes[0][1], float)


def test_get_chord():
    """Test chord generation."""
    from music_ai_core.elements import get_chord
    notes = get_chord("C", "major", octave=4)
    assert len(notes) == 3
    # Each note is a (name, frequency) tuple
    assert notes[0][0] == "C4"
    assert isinstance(notes[0][1], float)


def test_interval_name():
    """Test interval naming."""
    from music_ai_core.elements import interval_name
    name = interval_name(7)
    assert isinstance(name, str)
    assert len(name) > 0


def test_dance_import():
    """Test that the dance module imports cleanly."""
    from music_ai_core.dance import (
        DANCE_GENRES,
        list_genres,
        genre_description,
    )
    assert len(DANCE_GENRES) > 0
    assert len(list_genres()) > 0
    genres = list_genres()
    assert isinstance(genres, list)
    desc = genre_description(genres[0])
    assert isinstance(desc, str)


def test_beat_generator():
    """Test beat generator initialization and basic pattern generation."""
    from music_ai_core.dance import BeatGenerator
    bg = BeatGenerator(sample_rate=44100)
    assert bg is not None


def test_learning_import():
    """Test that the learning module imports cleanly."""
    from music_ai_core.learning import (
        LESSONS,
        list_lessons,
        list_exercise_types,
    )
    assert len(LESSONS) > 0
    assert len(list_lessons()) > 0
    assert len(list_exercise_types()) > 0


def test_learning_session():
    """Test learning session creation and lesson start."""
    from music_ai_core.learning import LearningSession
    session = LearningSession(student_id="test_student")
    assert session is not None
    lesson = session.start_lesson("el_01")
    assert lesson.id == "el_01"
    assert lesson.track == "elements"


def test_artist_mode_import():
    """Test that the artist_mode module imports cleanly."""
    from music_ai_core.artist_mode import (
        STYLE_PRESETS,
        list_styles,
        list_section_types,
    )
    assert len(STYLE_PRESETS) > 0
    assert len(list_styles()) > 0
    assert len(list_section_types()) > 0


def test_orchestrator_import():
    """Test that the orchestrator module imports and initializes cleanly."""
    from music_ai_core.orchestrator import ModuleOrchestrator
    orchestrator = ModuleOrchestrator()
    assert orchestrator is not None
    status = orchestrator.get_module_status()
    assert isinstance(status, dict)


def test_config_import():
    """Test that the config module imports and default config works."""
    from music_ai_core.config import get_default_config
    config = get_default_config()
    assert config is not None
    config_dict = config.get_config_dict()
    assert isinstance(config_dict, dict)
    assert len(config_dict) > 0


def test_music_ai_core_package():
    """Test the top-level music_ai_core package exports."""
    import music_ai_core
    assert hasattr(music_ai_core, "get_scale")
    assert hasattr(music_ai_core, "BeatGenerator")
    assert hasattr(music_ai_core, "LearningSession")
    assert hasattr(music_ai_core, "ArtistMode")

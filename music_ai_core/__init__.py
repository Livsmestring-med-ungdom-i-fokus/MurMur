from music_ai_core.audio import load_audio, mel_spectrogram, reconstruct_audio, save_audio
from music_ai_core.model import SimpleAutoencoder, ConvAutoencoder, get_model
from music_ai_core.live_studio import LiveMusicStudio, InstrumentSynthesizer, EffectsProcessor
from music_ai_core.chatgpt_integration import ChatGPTModule
from music_ai_core.orchestrator import ModuleOrchestrator, ModuleState
from music_ai_core.config import (
    AudioConfig,
    StudioConfig,
    ChatGPTConfig,
    ModelConfig,
    SystemConfig,
    get_default_config,
)

__version__ = "0.2.0"

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
)

from music_ai_core.vocal import VocalSynthesizer, VOWEL_FORMANTS, solfege_to_syllables

from music_ai_core.dance import (
    DANCE_GENRES,
    DrumSynthesizer,
    BeatGenerator,
    list_genres,
    genre_description,
)

from music_ai_core.artist_mode import (
    ArtistMode,
    Arrangement,
    Section,
    STYLE_PRESETS,
    list_styles,
    list_section_types,
)

from music_ai_core.learning import (
    LearningSession,
    ExerciseGenerator,
    StudentProgress,
    LESSONS,
    list_lessons,
    list_exercise_types,
)

__all__ = [
    # core audio/model/studio/orchestration/config
    "load_audio", "mel_spectrogram", "reconstruct_audio", "save_audio",
    "SimpleAutoencoder", "ConvAutoencoder", "get_model",
    "LiveMusicStudio", "InstrumentSynthesizer", "EffectsProcessor",
    "ChatGPTModule",
    "ModuleOrchestrator", "ModuleState",
    "AudioConfig", "StudioConfig", "ChatGPTConfig", "ModelConfig",
    "SystemConfig", "get_default_config",
    # elements
    "NOTE_FREQUENCIES", "ALL_NOTE_NAMES", "SCALE_PATTERNS", "CHORD_INTERVALS",
    "RHYTHM_PATTERNS", "get_scale", "get_chord", "scale_frequencies",
    "chord_frequencies", "melody_from_scale", "interval_name",
    "list_scales", "list_chords", "list_rhythms",
    # vocal
    "VocalSynthesizer", "VOWEL_FORMANTS", "solfege_to_syllables",
    # dance
    "DANCE_GENRES", "DrumSynthesizer", "BeatGenerator",
    "list_genres", "genre_description",
    # artist_mode
    "ArtistMode", "Arrangement", "Section", "STYLE_PRESETS",
    "list_styles", "list_section_types",
    # learning
    "LearningSession", "ExerciseGenerator", "StudentProgress",
    "LESSONS", "list_lessons", "list_exercise_types",
]

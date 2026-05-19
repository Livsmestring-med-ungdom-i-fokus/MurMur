import numpy as np
import pytest

from music_ai_core import (
    ChatGPTModule,
    LiveMusicStudio,
    ModuleOrchestrator,
    SimpleAutoencoder,
    get_default_config,
    load_audio,
    mel_spectrogram,
    reconstruct_audio,
)


def test_package_exports_are_available():
    assert callable(load_audio)
    assert callable(mel_spectrogram)
    assert callable(reconstruct_audio)
    assert SimpleAutoencoder is not None
    assert LiveMusicStudio is not None
    assert ModuleOrchestrator is not None
    assert ChatGPTModule is not None
    assert callable(get_default_config)


def test_reconstruct_audio_validates_shape():
    with pytest.raises(ValueError, match="2D mel spectrogram"):
        reconstruct_audio(np.ones(10))


def test_reconstruct_audio_validates_iterations():
    with pytest.raises(ValueError, match="positive integer"):
        reconstruct_audio(np.ones((80, 5)), iterations=0)


def test_generate_track_handles_empty_note_sequence():
    studio = LiveMusicStudio()
    output = studio.generate_track("track_0", [])
    assert output.size == 0
    assert studio.tracks["track_0"].size == 0


def test_generate_track_rejects_invalid_note_values():
    studio = LiveMusicStudio()
    with pytest.raises(ValueError, match="duration must be positive"):
        studio.generate_track("track_0", [(440.0, 0.0)])

    with pytest.raises(ValueError, match="frequency must be positive"):
        studio.generate_track("track_0", [(0.0, 0.5)])

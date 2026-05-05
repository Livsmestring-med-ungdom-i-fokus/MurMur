"""Tests for music_ai_core.config — system configuration manager."""

import json
import tempfile
import os
import pytest
from music_ai_core.config import (
    AudioConfig,
    StudioConfig,
    ChatGPTConfig,
    ModelConfig,
    SystemConfig,
    get_default_config,
)


class TestAudioConfig:
    def test_default_sample_rate(self):
        cfg = AudioConfig()
        assert cfg.sample_rate == 44100

    def test_default_channels(self):
        cfg = AudioConfig()
        assert cfg.channels == 2

    def test_custom_values(self):
        cfg = AudioConfig(sample_rate=48000, channels=1)
        assert cfg.sample_rate == 48000
        assert cfg.channels == 1


class TestStudioConfig:
    def test_default_tempo(self):
        cfg = StudioConfig()
        assert cfg.tempo == 120

    def test_default_time_signature(self):
        cfg = StudioConfig()
        assert cfg.time_signature == (4, 4)


class TestSystemConfig:
    def test_default_config_has_all_sections(self):
        cfg = SystemConfig()
        assert hasattr(cfg, "audio")
        assert hasattr(cfg, "studio")
        assert hasattr(cfg, "chatgpt")
        assert hasattr(cfg, "model")

    def test_get_config_dict_has_all_keys(self):
        cfg = SystemConfig()
        d = cfg.get_config_dict()
        assert set(d.keys()) >= {"audio", "studio", "chatgpt", "model", "custom"}

    def test_save_and_load_roundtrip(self):
        cfg = SystemConfig()
        cfg.audio.sample_rate = 48000
        cfg.studio.tempo = 140
        cfg.chatgpt.enabled = True

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            tmp_path = f.name

        try:
            cfg.save_to_file(tmp_path)
            loaded = SystemConfig()
            loaded.load_from_file(tmp_path)
            assert loaded.audio.sample_rate == 48000
            assert loaded.studio.tempo == 140
            assert loaded.chatgpt.enabled is True
        finally:
            os.unlink(tmp_path)

    def test_load_from_nonexistent_file_raises(self):
        cfg = SystemConfig()
        with pytest.raises(FileNotFoundError):
            cfg.load_from_file("/nonexistent/path/config.json")

    def test_save_creates_parent_dirs(self):
        cfg = SystemConfig()
        with tempfile.TemporaryDirectory() as tmpdir:
            nested_path = os.path.join(tmpdir, "nested", "deep", "config.json")
            cfg.save_to_file(nested_path)
            assert os.path.exists(nested_path)

    def test_saved_file_is_valid_json(self):
        cfg = SystemConfig()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            tmp_path = f.name
        try:
            cfg.save_to_file(tmp_path)
            with open(tmp_path) as f:
                data = json.load(f)
            assert "audio" in data
        finally:
            os.unlink(tmp_path)

    def test_load_partial_config_keeps_defaults_for_missing(self):
        partial = {"audio": {"sample_rate": 96000, "channels": 1,
                              "bit_depth": 16, "buffer_size": 2048}}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(partial, f)
            tmp_path = f.name
        try:
            cfg = SystemConfig()
            cfg.load_from_file(tmp_path)
            assert cfg.audio.sample_rate == 96000
            # Studio, chatgpt, model should retain defaults
            assert cfg.studio.tempo == 120
        finally:
            os.unlink(tmp_path)


class TestGetDefaultConfig:
    def test_returns_system_config(self):
        cfg = get_default_config()
        assert isinstance(cfg, SystemConfig)

    def test_default_audio_sample_rate(self):
        cfg = get_default_config()
        assert cfg.audio.sample_rate == 44100

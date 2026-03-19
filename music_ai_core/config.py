"""
Configuration for Music AI Studio

Manage system settings and module configurations.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
import json
from pathlib import Path


@dataclass
class AudioConfig:
    """Audio configuration."""
    sample_rate: int = 44100
    channels: int = 2
    bit_depth: int = 24
    buffer_size: int = 4096


@dataclass
class StudioConfig:
    """Studio configuration."""
    num_tracks: int = 8
    max_tracks: int = 32
    tempo: int = 120
    time_signature: tuple = (4, 4)


@dataclass
class ChatGPTConfig:
    """ChatGPT module configuration."""
    enabled: bool = False
    model: str = "gpt-4"
    max_tokens: int = 1000
    temperature: float = 0.7


@dataclass
class ModelConfig:
    """AI Model configuration."""
    model_type: str = "autoencoder"
    latent_dim: int = 128
    seq_len: int = 128
    n_mels: int = 80


class SystemConfig:
    """System configuration manager."""
    
    def __init__(self):
        """Initialize configuration."""
        self.audio = AudioConfig()
        self.studio = StudioConfig()
        self.chatgpt = ChatGPTConfig()
        self.model = ModelConfig()
        self.custom: Dict[str, Any] = {}
    
    def load_from_file(self, filepath: str) -> None:
        """
        Load configuration from JSON file.
        
        Args:
            filepath: Path to config file
        """
        config_path = Path(filepath)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {filepath}")
        
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        
        # Load sections
        if "audio" in config_data:
            audio_cfg = config_data["audio"]
            self.audio = AudioConfig(**audio_cfg)
        
        if "studio" in config_data:
            studio_cfg = config_data["studio"]
            self.studio = StudioConfig(**studio_cfg)
        
        if "chatgpt" in config_data:
            chatgpt_cfg = config_data["chatgpt"]
            self.chatgpt = ChatGPTConfig(**chatgpt_cfg)
        
        if "model" in config_data:
            model_cfg = config_data["model"]
            self.model = ModelConfig(**model_cfg)
        
        self.custom = config_data.get("custom", {})
    
    def save_to_file(self, filepath: str) -> None:
        """
        Save configuration to JSON file.
        
        Args:
            filepath: Path to save config
        """
        config_data = {
            "audio": {
                "sample_rate": self.audio.sample_rate,
                "channels": self.audio.channels,
                "bit_depth": self.audio.bit_depth,
                "buffer_size": self.audio.buffer_size,
            },
            "studio": {
                "num_tracks": self.studio.num_tracks,
                "max_tracks": self.studio.max_tracks,
                "tempo": self.studio.tempo,
                "time_signature": self.studio.time_signature,
            },
            "chatgpt": {
                "enabled": self.chatgpt.enabled,
                "model": self.chatgpt.model,
                "max_tokens": self.chatgpt.max_tokens,
                "temperature": self.chatgpt.temperature,
            },
            "model": {
                "model_type": self.model.model_type,
                "latent_dim": self.model.latent_dim,
                "seq_len": self.model.seq_len,
                "n_mels": self.model.n_mels,
            },
            "custom": self.custom
        }
        
        config_path = Path(filepath)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    def get_config_dict(self) -> Dict[str, Any]:
        """Get full configuration as dictionary."""
        return {
            "audio": self.audio.__dict__,
            "studio": self.studio.__dict__,
            "chatgpt": self.chatgpt.__dict__,
            "model": self.model.__dict__,
            "custom": self.custom
        }


# Default configuration
def get_default_config() -> SystemConfig:
    """Get default system configuration."""
    return SystemConfig()

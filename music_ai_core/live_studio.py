"""
Live Music Production Studio Module

Enables real-time music generation and synthesis capabilities.
"""

import numpy as np
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
import threading
from collections import deque


@dataclass
class AudioBuffer:
    """Audio buffer for real-time streaming."""
    sample_rate: int
    channels: int
    max_size: int = 44100  # 1 second at 44.1kHz
    
    def __post_init__(self):
        self._buffer = deque(maxlen=self.max_size)
        self._lock = threading.Lock()
    
    def write(self, data: np.ndarray) -> None:
        """Write audio data to buffer."""
        with self._lock:
            for sample in data:
                self._buffer.append(sample)
    
    def read(self, frames: int) -> np.ndarray:
        """Read audio frames from buffer."""
        with self._lock:
            if len(self._buffer) < frames:
                return np.zeros(frames)
            return np.array([self._buffer.popleft() for _ in range(frames)])
    
    def clear(self) -> None:
        """Clear buffer."""
        with self._lock:
            self._buffer.clear()


class InstrumentSynthesizer:
    """Synthesizer for generating instrument sounds."""
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.instrument_type = "synth"
        self.parameters = {
            "attack": 0.01,
            "decay": 0.1,
            "sustain": 0.7,
            "release": 0.3,
            "cutoff": 1000.0,
            "resonance": 0.5
        }
    
    def synthesize_note(self, frequency: float, duration: float, 
                       waveform: str = "sine") -> np.ndarray:
        """
        Synthesize a musical note.
        
        Args:
            frequency: Note frequency in Hz
            duration: Duration in seconds
            waveform: Type of waveform (sine, square, sawtooth, triangle)
            
        Returns:
            Audio samples as numpy array
        """
        samples = np.arange(int(self.sample_rate * duration)) / self.sample_rate
        
        if waveform == "sine":
            signal = np.sin(2 * np.pi * frequency * samples)
        elif waveform == "square":
            signal = np.sign(np.sin(2 * np.pi * frequency * samples))
        elif waveform == "sawtooth":
            signal = 2 * (samples * frequency - np.floor(samples * frequency + 0.5))
        elif waveform == "triangle":
            signal = 4 * np.abs((samples * frequency - np.floor(samples * frequency + 0.75)) - 0.5) - 1
        else:
            signal = np.sin(2 * np.pi * frequency * samples)
        
        # Apply ADSR envelope
        envelope = self._envelope_adsr(len(signal), duration)
        return signal * envelope * 0.3  # Scale to 0.3 amplitude
    
    def _envelope_adsr(self, length: int, duration: float) -> np.ndarray:
        """Generate ADSR envelope."""
        attack_len = int(self.parameters["attack"] * self.sample_rate)
        decay_len = int(self.parameters["decay"] * self.sample_rate)
        release_len = int(self.parameters["release"] * self.sample_rate)
        sustain_len = length - attack_len - decay_len - release_len
        
        envelope = np.concatenate([
            np.linspace(0, 1, max(1, attack_len)),
            np.linspace(1, self.parameters["sustain"], max(1, decay_len)),
            np.full(max(0, sustain_len), self.parameters["sustain"]),
            np.linspace(self.parameters["sustain"], 0, max(1, release_len))
        ])
        
        return envelope[:length]


class EffectsProcessor:
    """Apply audio effects to tracks."""
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
    
    def add_reverb(self, audio: np.ndarray, decay: float = 0.5) -> np.ndarray:
        """Simple reverb effect."""
        delay_samples = int(0.05 * self.sample_rate)  # 50ms delay
        delayed = np.concatenate([np.zeros(delay_samples), audio])
        return audio + decay * delayed[:len(audio)]
    
    def add_delay(self, audio: np.ndarray, delay_time: float = 0.25, 
                  feedback: float = 0.3) -> np.ndarray:
        """Add delay effect."""
        delay_samples = int(delay_time * self.sample_rate)
        delayed = np.concatenate([np.zeros(delay_samples), audio])
        return audio + feedback * delayed[:len(audio)]
    
    def add_compression(self, audio: np.ndarray, threshold: float = 0.6, 
                       ratio: float = 4.0) -> np.ndarray:
        """Simple dynamic range compression."""
        above_threshold = np.abs(audio) > threshold
        compressed = audio.copy()
        compressed[above_threshold] *= (1 / ratio)
        return compressed
    
    def normalize(self, audio: np.ndarray, target: float = 0.9) -> np.ndarray:
        """Normalize audio to target peak level."""
        peak = np.max(np.abs(audio))
        if peak > 0:
            return audio * (target / peak)
        return audio


class LiveMusicStudio:
    """Main live music production studio interface."""
    
    def __init__(self, sample_rate: int = 44100, num_tracks: int = 8):
        self.sample_rate = sample_rate
        self.num_tracks = num_tracks
        self.is_recording = False
        self.is_playing = False
        
        # Track management
        self.tracks: Dict[str, np.ndarray] = {}
        self.track_buffers: Dict[str, AudioBuffer] = {}
        self.track_parameters: Dict[str, Dict[str, Any]] = {}
        
        # Processors
        self.synthesizer = InstrumentSynthesizer(sample_rate)
        self.effects = EffectsProcessor(sample_rate)
        
        # Master settings
        self.master_volume = 1.0
        self.tempo = 120
        self.time_signature = (4, 4)
        
        self._initialize_tracks()
    
    def _initialize_tracks(self) -> None:
        """Initialize all tracks."""
        for i in range(self.num_tracks):
            track_name = f"track_{i}"
            self.tracks[track_name] = np.array([])
            self.track_buffers[track_name] = AudioBuffer(self.sample_rate, 1)
            self.track_parameters[track_name] = {
                "name": track_name,
                "muted": False,
                "volume": 1.0,
                "pan": 0.0,
                "effects": {}
            }
    
    def record_track(self, track_name: str, audio: np.ndarray) -> None:
        """Record audio to a track."""
        if track_name not in self.tracks:
            raise ValueError(f"Track {track_name} not found")
        
        self.tracks[track_name] = audio
    
    def generate_track(self, track_name: str, notes: List[Tuple[float, float]], 
                      waveform: str = "sine") -> np.ndarray:
        """
        Generate a track from note sequence.
        
        Args:
            track_name: Target track
            notes: List of (frequency, duration) tuples
            waveform: Waveform type
            
        Returns:
            Generated audio
        """
        audio_segments = []
        for freq, duration in notes:
            segment = self.synthesizer.synthesize_note(freq, duration, waveform)
            audio_segments.append(segment)
        
        track_audio = np.concatenate(audio_segments)
        self.record_track(track_name, track_audio)
        return track_audio
    
    def apply_effect(self, track_name: str, effect_type: str, **kwargs) -> None:
        """
        Apply audio effect to track.
        
        Args:
            track_name: Target track
            effect_type: Type of effect (reverb, delay, compression)
            **kwargs: Effect parameters
        """
        if track_name not in self.tracks:
            raise ValueError(f"Track {track_name} not found")
        
        audio = self.tracks[track_name]
        
        if effect_type == "reverb":
            audio = self.effects.add_reverb(audio, kwargs.get("decay", 0.5))
        elif effect_type == "delay":
            audio = self.effects.add_delay(audio, kwargs.get("delay_time", 0.25))
        elif effect_type == "compression":
            audio = self.effects.add_compression(audio, kwargs.get("threshold", 0.6))
        
        self.tracks[track_name] = audio
        self.track_parameters[track_name]["effects"][effect_type] = kwargs
    
    def set_track_volume(self, track_name: str, volume: float) -> None:
        """Set track volume (0.0 to 1.0)."""
        if track_name not in self.tracks:
            raise ValueError(f"Track {track_name} not found")
        
        volume = max(0.0, min(1.0, volume))
        self.tracks[track_name] *= volume
        self.track_parameters[track_name]["volume"] = volume
    
    def set_track_pan(self, track_name: str, pan: float) -> None:
        """Set track panning (-1.0 left to 1.0 right)."""
        if track_name not in self.tracks:
            raise ValueError(f"Track {track_name} not found")
        
        pan = max(-1.0, min(1.0, pan))
        self.track_parameters[track_name]["pan"] = pan
    
    def mix(self) -> np.ndarray:
        """
        Mix all tracks to stereo master.
        
        Returns:
            Mixed stereo audio
        """
        # Find max track length
        max_len = max([len(audio) for audio in self.tracks.values()], default=0)
        
        if max_len == 0:
            return np.array([])
        
        # Initialize mono mix
        mono_mix = np.zeros(max_len)
        
        for track_name, audio in self.tracks.items():
            if not self.track_parameters[track_name]["muted"]:
                padded = np.pad(audio, (0, max_len - len(audio)))
                mono_mix += padded
        
        # Normalize
        mono_mix = self.effects.normalize(mono_mix, 0.9)
        
        # Apply master volume
        mono_mix *= self.master_volume
        
        # Create stereo
        stereo = np.stack([mono_mix, mono_mix])
        
        return stereo
    
    def set_tempo(self, bpm: int) -> None:
        """Set studio tempo in BPM."""
        self.tempo = bpm
    
    def set_time_signature(self, numerator: int, denominator: int) -> None:
        """Set time signature."""
        self.time_signature = (numerator, denominator)
    
    def mute_track(self, track_name: str) -> None:
        """Mute a track."""
        if track_name in self.track_parameters:
            self.track_parameters[track_name]["muted"] = True
    
    def unmute_track(self, track_name: str) -> None:
        """Unmute a track."""
        if track_name in self.track_parameters:
            self.track_parameters[track_name]["muted"] = False
    
    def get_studio_state(self) -> Dict[str, Any]:
        """Get current studio state."""
        return {
            "tempo": self.tempo,
            "time_signature": self.time_signature,
            "master_volume": self.master_volume,
            "tracks": self.track_parameters,
            "num_tracks": self.num_tracks
        }

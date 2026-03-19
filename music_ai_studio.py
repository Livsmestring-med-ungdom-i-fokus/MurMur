"""
Music AI Studio Application

Main entry point for the modular music production system.
Integrates ChatGPT, Live Studio, and ML models.
"""

import argparse
from typing import Optional
import sys
from pathlib import Path

from music_ai_core.orchestrator import ModuleOrchestrator
from music_ai_core.chatgpt_integration import ChatGPTModule
from music_ai_core.live_studio import LiveMusicStudio
from music_ai_core.model import SimpleAutoencoder


class MusicAIStudio:
    """Main application class for music AI studio."""
    
    def __init__(self, use_chatgpt: bool = False, sample_rate: int = 44100):
        """
        Initialize Music AI Studio.
        
        Args:
            use_chatgpt: Whether to enable ChatGPT integration
            sample_rate: Audio sample rate in Hz
        """
        self.orchestrator = ModuleOrchestrator()
        self.sample_rate = sample_rate
        
        # Initialize modules
        self.studio = LiveMusicStudio(sample_rate=sample_rate, num_tracks=8)
        self.orchestrator.register_module("studio", self.studio)
        
        # ChatGPT module (optional)
        if use_chatgpt:
            try:
                self.chatgpt = ChatGPTModule()
                self.orchestrator.register_module("chatgpt", self.chatgpt)
            except ValueError as e:
                print(f"⚠️  ChatGPT module disabled: {e}")
                self.chatgpt = None
        else:
            self.chatgpt = None
        
        # AI Model
        self.model = SimpleAutoencoder(n_mels=80, latent_dim=128, seq_len=128)
        self.orchestrator.register_module("model", self.model)
        
        print("✓ Music AI Studio initialized")
        self._print_system_status()
    
    def get_music_prompt(self, prompt: str) -> dict:
        """
        Process a music generation prompt.
        
        Args:
            prompt: User's music request
            
        Returns:
            Processing result
        """
        print(f"\n🎵 Processing: {prompt}")
        result = self.orchestrator.process_music_request(prompt)
        return result
    
    def create_composition(self, name: str, description: str) -> dict:
        """
        Create a new composition.
        
        Args:
            name: Composition name
            description: Composition description
            
        Returns:
            Composition metadata
        """
        composition = {
            "name": name,
            "description": description,
            "tracks": self.studio.get_studio_state()
        }
        
        if self.chatgpt:
            interpretation = self.chatgpt.interpret_music_prompt(description)
            composition["interpretation"] = interpretation
        
        return composition
    
    def generate_track(self, track_name: str, notes_description: str) -> None:
        """
        Generate a music track.
        
        Args:
            track_name: Name of track
            notes_description: Description of notes to generate
        """
        # Simple note frequency mapping (C major scale)
        note_map = {
            "C": 261.63, "D": 293.66, "E": 329.63, "F": 349.23,
            "G": 391.99, "A": 440.0, "B": 493.88
        }
        
        # Parse simple note sequence (e.g., "C D E F G")
        note_names = notes_description.split()
        notes = []
        
        for note_name in note_names:
            if note_name in note_map:
                notes.append((note_map[note_name], 0.5))  # 0.5 second per note
        
        if notes:
            self.studio.generate_track(track_name, notes, waveform="sine")
            print(f"✓ Generated {track_name} with {len(notes)} notes")
    
    def add_effect_to_track(self, track_name: str, effect: str, **params) -> None:
        """
        Add effect to track.
        
        Args:
            track_name: Target track
            effect: Effect type (reverb, delay, compression)
            **params: Effect parameters
        """
        self.studio.apply_effect(track_name, effect, **params)
        print(f"✓ Applied {effect} to {track_name}")
    
    def set_studio_tempo(self, bpm: int) -> None:
        """Set studio tempo."""
        self.studio.set_tempo(bpm)
        print(f"✓ Tempo set to {bpm} BPM")
    
    def get_studio_state(self) -> dict:
        """Get current studio state."""
        return self.studio.get_studio_state()
    
    def _print_system_status(self) -> None:
        """Print system status."""
        status = self.orchestrator.get_system_info()
        print("\n📊 System Status:")
        print(f"   Modules: {', '.join(status['modules'])}")
        print(f"   Sample Rate: {self.sample_rate} Hz")

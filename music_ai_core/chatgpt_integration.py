"""
ChatGPT Integration Module for Music AI

Enables collaboration with OpenAI's ChatGPT for:
- Music generation prompts interpretation
- Creative suggestions
- Live studio direction
"""

import os
from typing import Optional, Dict, Any, List
import json


class ChatGPTModule:
    """Interface for ChatGPT integration in music production."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize ChatGPT module.
        
        Args:
            api_key: OpenAI API key. If None, reads from OPENAI_API_KEY env var
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set and no api_key provided")
        
        self.conversation_history: List[Dict[str, str]] = []
        self.model = "gpt-4"
        
    def interpret_music_prompt(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Interpret a natural language music production prompt.
        
        Args:
            prompt: User's music production request
            context: Optional context about current project
            
        Returns:
            Structured interpretation with music parameters
        """
        system_message = """You are a music production AI assistant. 
When given a music production request, respond with a JSON object containing:
- genre: music genre
- tempo: suggested BPM (integer)
- mood: emotional tone
- instruments: list of suggested instruments
- production_tips: list of production advice
"""
        
        self.conversation_history.append({
            "role": "user",
            "content": prompt
        })
        
        # This is a placeholder - in production, make actual API call to OpenAI
        interpretation = self._parse_response_to_json(prompt)
        
        self.conversation_history.append({
            "role": "assistant",
            "content": json.dumps(interpretation)
        })
        
        return interpretation
    
    def get_creative_suggestion(self, music_state: Dict[str, Any]) -> str:
        """
        Get creative suggestions based on current music state.
        
        Args:
            music_state: Current state of the music production
            
        Returns:
            Creative suggestion string
        """
        prompt = f"Given this music state: {json.dumps(music_state)}, what's your next creative suggestion?"
        
        self.conversation_history.append({
            "role": "user",
            "content": prompt
        })
        
        # Placeholder response
        suggestion = "Try adding a reverb effect to the vocals for more depth and space"
        
        self.conversation_history.append({
            "role": "assistant",
            "content": suggestion
        })
        
        return suggestion
    
    def generate_music_parameters(self, description: str) -> Dict[str, Any]:
        """
        Generate detailed music parameters from description.
        
        Args:
            description: Human-readable music description
            
        Returns:
            Dictionary with music parameters (BPM, key, instruments, etc.)
        """
        params = {
            "tempo": 120,
            "key": "C minor",
            "time_signature": "4/4",
            "instruments": ["drums", "bass", "synth"],
            "effects": ["reverb", "delay"],
            "duration": 120  # seconds
        }
        
        self.conversation_history.append({
            "role": "user",
            "content": f"Music description: {description}"
        })
        
        return params
    
    def _parse_response_to_json(self, prompt: str) -> Dict[str, Any]:
        """Parse prompt into music parameters."""
        # Default interpretation
        return {
            "genre": "electronic",
            "tempo": 120,
            "mood": "energetic",
            "instruments": ["synth", "drums", "bass"],
            "production_tips": [
                "Start with a strong kick pattern",
                "Layer atmospheric pads underneath"
            ]
        }
    
    def reset_conversation(self):
        """Reset conversation history."""
        self.conversation_history = []
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get full conversation history."""
        return self.conversation_history.copy()

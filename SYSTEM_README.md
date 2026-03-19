# Music AI Studio - Modular AI Music Production System

A comprehensive modular AI system for live music production that integrates ChatGPT, advanced audio synthesis, and machine learning models.

## 🎵 Features

### Core Modules

1. **Live Music Studio** - Real-time music production interface
   - Multi-track recording and synthesis
   - Instrument synthesis (sine, square, sawtooth, triangle waves)
   - Professional audio effects (reverb, delay, compression)
   - Master volume and effects control

2. **ChatGPT Integration** - Creative AI direction
   - Natural language music prompt interpretation
   - Automatic parameter extraction (tempo, mood, instruments)
   - Conversation history management
   - Creative suggestions based on music state

3. **Module Orchestrator** - System coordination
   - Module registration and lifecycle management
   - Event-based architecture
   - Collaborative task execution
   - Session management and logging

4. **AI Model Core** - Machine learning foundation
   - Autoencoder for audio feature extraction
   - Mel-spectrogram processing
   - Model training pipeline

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or install torch manually if needed
pip install torch librosa numpy
```

### Basic Usage

```python
from music_ai_studio import MusicAIStudio

# Initialize studio
studio = MusicAIStudio(use_chatgpt=False)

# Set tempo
studio.set_studio_tempo(120)

# Generate a track
studio.generate_track("track_0", "C D E F G")

# Add effects
studio.add_effect_to_track("track_0", "reverb", decay=0.5)

# Mix and output
mixed = studio.studio.mix()
```

### CLI Usage

```bash
# Interactive mode
python cli.py --interactive

# Process a music prompt
python cli.py --prompt "upbeat electronic dance track"

# With ChatGPT integration (requires OPENAI_API_KEY)
python cli.py --interactive --chatgpt

# Show system information
python cli.py --info

# Run examples
python cli.py --example 1
python cli.py --example 2
python cli.py --example 3
python cli.py --example 4
python cli.py --example 5
```

## 📚 Module Architecture

### Live Music Studio (`music_ai_core/live_studio.py`)

```python
studio = LiveMusicStudio(sample_rate=44100, num_tracks=8)

# Track management
studio.generate_track("track_0", [(440, 0.5), (880, 0.5)])
studio.record_track("track_1", audio_array)

# Effects
studio.apply_effect("track_0", "reverb", decay=0.5)
studio.apply_effect("track_0", "delay", delay_time=0.25, feedback=0.3)
studio.apply_effect("track_0", "compression", threshold=0.6, ratio=4.0)

# Mixing
mixed_audio = studio.mix()
```

### ChatGPT Integration (`music_ai_core/chatgpt_integration.py`)

```python
from music_ai_core import ChatGPTModule

chatgpt = ChatGPTModule(api_key="your-openai-key")

# Interpret prompts
interpretation = chatgpt.interpret_music_prompt(
    "Create upbeat electronic music"
)

# Get suggestions
suggestion = chatgpt.get_creative_suggestion(music_state)

# Generate parameters
params = chatgpt.generate_music_parameters("Ambient chill vibes")
```

### Module Orchestrator (`music_ai_core/orchestrator.py`)

```python
from music_ai_core import ModuleOrchestrator

orchestrator = ModuleOrchestrator()

# Register modules
orchestrator.register_module("studio", studio)
orchestrator.register_module("chatgpt", chatgpt)
orchestrator.register_module("model", model)

# Process requests
result = orchestrator.process_music_request("happy upbeat track")

# Collaborate
collab_result = orchestrator.collaborate_modules(
    "compose", 
    {"style": "electronic"}
)

# Monitor
status = orchestrator.get_module_status()
events = orchestrator.get_event_log()
```

## 🎛️ Configuration

Create a config file `config.json`:

```json
{
  "audio": {
    "sample_rate": 44100,
    "channels": 2,
    "bit_depth": 24,
    "buffer_size": 4096
  },
  "studio": {
    "num_tracks": 8,
    "max_tracks": 32,
    "tempo": 120,
    "time_signature": [4, 4]
  },
  "chatgpt": {
    "enabled": true,
    "model": "gpt-4",
    "max_tokens": 1000,
    "temperature": 0.7
  },
  "model": {
    "model_type": "autoencoder",
    "latent_dim": 128,
    "seq_len": 128,
    "n_mels": 80
  }
}
```

Load config:

```python
from music_ai_core.config import SystemConfig

config = SystemConfig()
config.load_from_file("config.json")
```

## 📋 Examples

### Example 1: Basic Workflow

```bash
python cli.py --example 1
```

### Example 2: ChatGPT Creative Direction

```bash
python cli.py --example 2
```

Requires `OPENAI_API_KEY` environment variable.

### Example 3: Effects Processing

```bash
python cli.py --example 3
```

### Example 4: Complete Composition

```bash
python cli.py --example 4
```

### Example 5: Module Orchestration

```bash
python cli.py --example 5
```

## 🔧 Advanced Usage

### Custom Effects Chain

```python
studio = MusicAIStudio()

# Generate track
studio.generate_track("track_0", "C D E F G")

# Chain effects
studio.add_effect_to_track("track_0", "reverb", decay=0.6)
studio.add_effect_to_track("track_0", "delay", delay_time=0.3, feedback=0.4)
studio.add_effect_to_track("track_0", "compression", threshold=0.7)

# Get final mix
mixed = studio.studio.mix()
```

### Event-Driven Architecture

```python
# Register event listener
def on_interpretation_complete(data):
    print(f"Interpreted as: {data['genre']}")

studio.orchestrator.on_event("interpretation_complete", on_interpretation_complete)

# Trigger event
studio.get_music_prompt("ambient electronic")
```

### Multi-Module Collaboration

```python
# Set up collaborative task
result = studio.orchestrator.collaborate_modules(
    task="compose",
    params={
        "style": "jazz",
        "duration_seconds": 120,
        "instruments": ["piano", "bass", "drums"]
    }
)

# Each module contributes
for module, contribution in result["results"].items():
    print(f"{module}: {contribution}")
```

## 🎓 System Architecture

```
┌─────────────────────────────────────┐
│      Music AI Studio (Main)          │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│     Module Orchestrator              │
├─────────────────────────────────────┤
│ • Module registration               │
│ • Event management                  │
│ • Collaboration coordination        │
└─────────────────────────────────────┘
           ↓↓↓
  ┌────────┴────────┬────────────┐
  ↓                 ↓            ↓
┌──────────┐  ┌──────────┐  ┌──────────┐
│  Studio  │  │ ChatGPT  │  │  Model   │
├──────────┤  ├──────────┤  ├──────────┤
│Synthesis │  │Creative  │  │Learning  │
│Effects   │  │Direction │  │Feature   │
│Mixing    │  │Prompts   │  │Extract   │
└──────────┘  └──────────┘  └──────────┘
```

## 📊 Audio Processing Pipeline

1. **Synthesis** - Generate raw audio signals
2. **Recording** - Capture external audio
3. **Effects** - Apply reverb, delay, compression
4. **Mixing** - Combine all tracks
5. **Normalization** - Ensure proper levels

## 🔐 Environment Variables

```bash
# OpenAI API key (for ChatGPT integration)
export OPENAI_API_KEY="your-api-key-here"
```

## 📝 License

MIT License - See LICENSE file

## 🤝 Contributing

Contributions welcome! Please follow existing code style and add tests for new features.

## 🎯 Roadmap

- [ ] Real-time audio streaming support
- [ ] DAW plugin integration (VST/AU)
- [ ] MIDI controller support
- [ ] Advanced synthesis (FM, granular, wavetable)
- [ ] Neural vocoder integration
- [ ] Preset management system
- [ ] Audio file export (WAV, MP3)
- [ ] Interactive web UI
- [ ] Collaborative session support

## 📞 Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Happy Music Making! 🎵**

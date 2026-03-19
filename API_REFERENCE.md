# Music AI Studio - API Reference

## Table of Contents
1. [LiveMusicStudio](#livemusic-studio)
2. [ChatGPTModule](#chatgpt-module)
3. [ModuleOrchestrator](#module-orchestrator)
4. [InstrumentSynthesizer](#instrument-synthesizer)
5. [EffectsProcessor](#effects-processor)

---

## LiveMusicStudio

Main interface for live music production.

### Constructor

```python
LiveMusicStudio(sample_rate: int = 44100, num_tracks: int = 8)
```

**Parameters:**
- `sample_rate` (int): Audio sample rate in Hz. Default: 44100
- `num_tracks` (int): Number of available tracks. Default: 8

### Methods

#### `generate_track(track_name: str, notes: List[Tuple[float, float]], waveform: str = "sine") -> np.ndarray`

Generate a track from note sequence.

**Parameters:**
- `track_name` (str): Name of target track
- `notes` (List[Tuple[float, float]]): List of (frequency, duration) tuples
- `waveform` (str): Waveform type: "sine", "square", "sawtooth", "triangle"

**Returns:**
- `np.ndarray`: Generated audio array

**Example:**
```python
notes = [(440, 0.5), (880, 0.5), (440, 1.0)]  # A4, A5 notes
audio = studio.generate_track("track_0", notes, waveform="sine")
```

#### `record_track(track_name: str, audio: np.ndarray) -> None`

Record audio to a track.

**Parameters:**
- `track_name` (str): Target track name
- `audio` (np.ndarray): Audio samples to record

#### `apply_effect(track_name: str, effect_type: str, **kwargs) -> None`

Apply audio effect to track.

**Parameters:**
- `track_name` (str): Target track
- `effect_type` (str): "reverb", "delay", or "compression"
- `**kwargs`: Effect-specific parameters

**Effects:**
- `reverb`: `decay` (0.0-1.0)
- `delay`: `delay_time` (float), `feedback` (0.0-1.0)
- `compression`: `threshold` (0.0-1.0), `ratio` (float)

**Example:**
```python
studio.apply_effect("track_0", "reverb", decay=0.5)
studio.apply_effect("track_0", "delay", delay_time=0.25, feedback=0.3)
```

#### `set_track_volume(track_name: str, volume: float) -> None`

Set track volume (0.0 to 1.0).

#### `set_track_pan(track_name: str, pan: float) -> None`

Set track panning (-1.0 left to 1.0 right).

#### `mute_track(track_name: str) -> None`

Mute a track.

#### `unmute_track(track_name: str) -> None`

Unmute a track.

#### `set_tempo(bpm: int) -> None`

Set studio tempo in BPM.

#### `set_time_signature(numerator: int, denominator: int) -> None`

Set time signature (e.g., 4/4, 3/4).

#### `mix() -> np.ndarray`

Mix all tracks to stereo master output.

**Returns:**
- `np.ndarray`: Stereo audio (shape: 2 x samples)

#### `get_studio_state() -> Dict[str, Any]`

Get current studio state.

**Returns:**
- Dictionary with tempo, tracks, and settings

---

## ChatGPTModule

AI-powered creative direction for music production.

### Constructor

```python
ChatGPTModule(api_key: Optional[str] = None)
```

**Parameters:**
- `api_key` (str): OpenAI API key. If None, reads from `OPENAI_API_KEY` env var

### Methods

#### `interpret_music_prompt(prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]`

Interpret natural language music prompt.

**Parameters:**
- `prompt` (str): User's music request
- `context` (Dict): Optional context about project

**Returns:**
- Dictionary with:
  - `genre` (str): Music genre
  - `tempo` (int): Suggested BPM
  - `mood` (str): Emotional tone
  - `instruments` (List[str]): Suggested instruments
  - `production_tips` (List[str]): Production advice

**Example:**
```python
result = chatgpt.interpret_music_prompt(
    "Create upbeat electronic dance music"
)
# Returns: {
#   "genre": "electronic",
#   "tempo": 128,
#   "mood": "energetic",
#   "instruments": ["synth", "drums", "bass"],
#   "production_tips": [...]
# }
```

#### `get_creative_suggestion(music_state: Dict[str, Any]) -> str`

Get creative suggestions based on current music state.

**Parameters:**
- `music_state` (Dict): Current production state

**Returns:**
- String with creative suggestion

#### `generate_music_parameters(description: str) -> Dict[str, Any]`

Generate detailed music parameters from description.

**Returns:**
- Dictionary with: `tempo`, `key`, `time_signature`, `instruments`, `effects`, `duration`

#### `reset_conversation() -> None`

Clear conversation history.

#### `get_conversation_history() -> List[Dict[str, str]]`

Get full conversation history.

---

## ModuleOrchestrator

Coordinates collaboration between modules.

### Constructor

```python
ModuleOrchestrator()
```

### Methods

#### `register_module(module_name: str, module_instance: Any) -> None`

Register a module.

**Parameters:**
- `module_name` (str): Unique identifier
- `module_instance` (Any): Module to register

#### `unregister_module(module_name: str) -> None`

Unregister a module.

#### `get_module(module_name: str) -> Any`

Retrieve a registered module.

#### `set_module_state(module_name: str, state: ModuleState) -> None`

Update module state.

**States:** `IDLE`, `PROCESSING`, `READY`, `ERROR`

#### `on_event(event_name: str, callback: Callable) -> None`

Register event listener.

**Parameters:**
- `event_name` (str): Event name
- `callback` (Callable): Function to call on event

**Example:**
```python
def on_complete(data):
    print(f"Complete: {data}")

orchestrator.on_event("interpretation_complete", on_complete)
```

#### `emit_event(event_name: str, data: Dict[str, Any]) -> None`

Emit an event and trigger callbacks.

#### `process_music_request(request: str) -> Dict[str, Any]`

Process complete music production request.

**Flow:**
1. ChatGPT interprets request
2. Studio prepares
3. Model generates
4. Mix output

**Returns:**
- Result dictionary with all stages

#### `collaborate_modules(task: str, params: Dict[str, Any]) -> Dict[str, Any]`

Execute collaborative task across modules.

**Parameters:**
- `task` (str): Task type (e.g., "compose", "refine")
- `params` (Dict): Task parameters

#### `save_session(filepath: str) -> None`

Save session to JSON file.

#### `load_session(filepath: str) -> None`

Load session from JSON file.

#### `get_module_status() -> Dict[str, str]`

Get status of all modules.

#### `get_event_log(limit: Optional[int] = None) -> List[Dict[str, Any]]`

Get event log.

#### `get_system_info() -> Dict[str, Any]`

Get system information and statistics.

---

## InstrumentSynthesizer

Generates musical notes and synthesized sounds.

### Constructor

```python
InstrumentSynthesizer(sample_rate: int = 44100)
```

### Methods

#### `synthesize_note(frequency: float, duration: float, waveform: str = "sine") -> np.ndarray`

Synthesize a musical note.

**Parameters:**
- `frequency` (float): Note frequency in Hz
- `duration` (float): Duration in seconds
- `waveform` (str): "sine", "square", "sawtooth", "triangle"

**Returns:**
- `np.ndarray`: Audio samples

**Example:**
```python
# Generate A4 note (440 Hz) for 1 second
audio = synth.synthesize_note(440, 1.0, waveform="sine")
```

---

## EffectsProcessor

Applies professional audio effects.

### Constructor

```python
EffectsProcessor(sample_rate: int = 44100)
```

### Methods

#### `add_reverb(audio: np.ndarray, decay: float = 0.5) -> np.ndarray`

Add reverb effect.

**Parameters:**
- `audio` (np.ndarray): Audio signal
- `decay` (float): Reverb decay (0.0-1.0)

#### `add_delay(audio: np.ndarray, delay_time: float = 0.25, feedback: float = 0.3) -> np.ndarray`

Add delay effect.

**Parameters:**
- `audio` (np.ndarray): Audio signal
- `delay_time` (float): Delay time in seconds
- `feedback` (float): Feedback amount (0.0-1.0)

#### `add_compression(audio: np.ndarray, threshold: float = 0.6, ratio: float = 4.0) -> np.ndarray`

Apply dynamic range compression.

**Parameters:**
- `audio` (np.ndarray): Audio signal
- `threshold` (float): Compression threshold (0.0-1.0)
- `ratio` (float): Compression ratio

#### `normalize(audio: np.ndarray, target: float = 0.9) -> np.ndarray`

Normalize audio to target peak level.

**Parameters:**
- `audio` (np.ndarray): Audio signal
- `target` (float): Target peak level (0.0-1.0)

---

## Configuration

### SystemConfig

Manage system settings.

```python
from music_ai_core.config import SystemConfig

config = SystemConfig()
config.load_from_file("config.json")
config.save_to_file("new_config.json")
config.get_config_dict()
```

---

## Constants & Defaults

### Note Frequencies (Hz)
- C4: 261.63
- D4: 293.66
- E4: 329.63
- F4: 349.23
- G4: 391.99
- A4: 440.0
- B4: 493.88

### Default Parameters
- **Sample Rate:** 44100 Hz
- **Channels:** 2 (stereo)
- **Bit Depth:** 24-bit
- **Buffer Size:** 4096 samples
- **Default Tempo:** 120 BPM
- **Default Time Signature:** 4/4

---

## Events

Common events emitted by the orchestrator:

- `module_registered` - Module was registered
- `module_unregistered` - Module was unregistered
- `state_change` - Module state changed
- `music_request_started` - Music request processing started
- `interpretation_complete` - ChatGPT interpretation done
- `studio_ready` - Studio is ready for production
- `generation_complete` - Model generation complete
- `music_request_completed` - Full request completed
- `collaboration_started` - Module collaboration started
- `collaboration_complete` - Collaboration finished
- `session_saved` - Session saved to file
- `session_loaded` - Session loaded from file

---

## Error Handling

All modules raise appropriate Python exceptions:

```python
try:
    studio.apply_effect("track_99", "reverb")
except ValueError:
    print("Track not found")

try:
    chatgpt = ChatGPTModule()
except ValueError:
    print("API key not configured")
```

---

## Examples

See [examples.py](examples.py) for complete working examples:
- Basic workflow
- ChatGPT integration
- Effects processing
- Complete composition
- Module orchestration

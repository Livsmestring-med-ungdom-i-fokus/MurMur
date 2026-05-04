"""
Music AI Studio Application

Main entry point for the modular music production system.
Integrates ChatGPT, Live Studio, ML models, and the five learning modules:
Elements, Vocal, Dance, Artist Mode, and Learning.
"""

from typing import Optional

from music_ai_core.orchestrator import ModuleOrchestrator
from music_ai_core.chatgpt_integration import ChatGPTModule
from music_ai_core.live_studio import LiveMusicStudio
from music_ai_core.model import SimpleAutoencoder
from music_ai_core.elements import get_scale, get_chord, melody_from_scale
from music_ai_core.vocal import VocalSynthesizer
from music_ai_core.dance import BeatGenerator, DANCE_GENRES
from music_ai_core.artist_mode import ArtistMode
from music_ai_core.learning import LearningSession


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

        # Vocal: vocal synthesizer
        self.vocal = VocalSynthesizer(sample_rate=sample_rate)
        self.orchestrator.register_module("vocal", self.vocal)

        # Dance: beat generator
        self.beat_generator = BeatGenerator(sample_rate=sample_rate)
        self.orchestrator.register_module("beat_generator", self.beat_generator)

        # Artist mode
        self.artist_mode = ArtistMode()
        self.orchestrator.register_module("artist_mode", self.artist_mode)

        # Learning session
        self.learning = LearningSession()
        self.orchestrator.register_module("learning", self.learning)

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

    # ------------------------------------------------------------------
    # Elements helpers
    # ------------------------------------------------------------------

    def get_scale(self, root: str, scale_type: str = "major", octave: int = 4) -> list:
        """Return the notes of a scale as (note_name, frequency) tuples."""
        return get_scale(root, scale_type, octave)

    def get_chord(self, root: str, chord_type: str = "major", octave: int = 4) -> list:
        """Return the notes of a chord as (note_name, frequency) tuples."""
        return get_chord(root, chord_type, octave)

    def generate_scale_melody(
        self,
        track_name: str,
        root: str = "C",
        scale_type: str = "major",
        octave: int = 4,
        rhythm: str = "quarter_notes",
        bpm: int = 120,
        waveform: str = "sine",
    ) -> None:
        """
        Generate a scale-based melody and write it to a studio track.

        Args:
            track_name: Target studio track
            root: Scale root note
            scale_type: Scale type (major, minor, pentatonic_major, …)
            octave: Starting octave
            rhythm: Rhythm pattern name
            bpm: Tempo
            waveform: Synthesizer waveform
        """
        notes = melody_from_scale(root, scale_type, octave, rhythm, bpm)
        self.studio.generate_track(track_name, notes, waveform=waveform)
        print(f"✓ Scale melody '{root} {scale_type}' → {track_name} ({len(notes)} notes)")

    # ------------------------------------------------------------------
    # Vocal helpers
    # ------------------------------------------------------------------

    def generate_vocal_line(
        self,
        track_name: str,
        syllables: list,
        frequencies: list,
        durations: list,
        vibrato_rate: float = 5.5,
        chorus: bool = False,
    ) -> None:
        """
        Synthesize a vocal line and write it to a studio track.

        Args:
            track_name: Target studio track
            syllables: List of syllable strings
            frequencies: Fundamental frequency per syllable (Hz)
            durations: Duration per syllable (seconds)
            vibrato_rate: Vibrato speed (Hz)
            chorus: Whether to apply chorus effect
        """
        audio = self.vocal.synthesize_vocal_line(
            syllables, frequencies, durations, vibrato_rate=vibrato_rate
        )
        if chorus:
            audio = self.vocal.add_chorus(audio)
        self.studio.record_track(track_name, audio)
        print(f"✓ Vocal line → {track_name} ({len(syllables)} syllables, "
              f"{len(audio)/self.sample_rate:.2f}s)")

    # ------------------------------------------------------------------
    # Dance helpers
    # ------------------------------------------------------------------

    def generate_beat(
        self,
        genre: str = "house",
        bpm: Optional[int] = None,
        bars: int = 4,
        humanize: float = 0.0,
    ) -> None:
        """
        Generate a drum beat for the given genre and write to dedicated tracks.

        Track names: ``beat_kick``, ``beat_snare``, ``beat_hihat_closed``,
        ``beat_hihat_open``, ``beat_clap``.

        Args:
            genre: Dance genre (house, techno, hip_hop, trap, …)
            bpm: Override genre default BPM
            bars: Number of bars to generate
            humanize: Timing randomness 0–1
        """
        tracks = self.beat_generator.generate_bar(genre, bpm=bpm, bars=bars, humanize=humanize)
        for voice, audio in tracks.items():
            track_name = f"beat_{voice}"
            self.studio.record_track(track_name, audio)
        genre_info = DANCE_GENRES[genre]
        actual_bpm = bpm or genre_info.default_bpm
        print(f"✓ Beat generated: {genre} @ {actual_bpm} BPM, {bars} bar(s)")

    # ------------------------------------------------------------------
    # Artist mode helpers
    # ------------------------------------------------------------------

    def build_arrangement(
        self,
        title: str = "Untitled",
        style: Optional[str] = None,
        key: Optional[str] = None,
        bpm: Optional[int] = None,
    ) -> dict:
        """
        Build a song arrangement using artist mode and return it as a dict.

        Args:
            title: Song title
            style: Style preset (pop, edm, jazz, hip_hop, classical, reggae)
            key: Override key
            bpm: Override BPM

        Returns:
            Arrangement data as a plain dict.
        """
        arrangement = self.artist_mode.build_arrangement(
            title=title, style=style, key=key, bpm=bpm
        )
        print(arrangement.summary())
        return arrangement.to_dict()

    def get_inspiration(self) -> dict:
        """Return a random creative inspiration prompt from artist mode."""
        inspiration = self.artist_mode.get_inspiration()
        print("\n💡 Inspiration:")
        for k, v in inspiration.items():
            print(f"   {k.capitalize()}: {v}")
        return inspiration

    # ------------------------------------------------------------------
    # Learning helpers
    # ------------------------------------------------------------------

    def start_lesson(self, lesson_id: str) -> dict:
        """
        Start a music theory lesson.

        Args:
            lesson_id: Lesson identifier (e.g. ``"el_01"``)

        Returns:
            Lesson metadata as a dict.
        """
        lesson = self.learning.start_lesson(lesson_id)
        print(f"\n📖 Lesson: {lesson.title} [{lesson.track} / {lesson.difficulty}]")
        print(f"   {lesson.description}")
        print(f"   Key concepts: {', '.join(lesson.key_concepts)}")
        return {
            "id": lesson.id,
            "title": lesson.title,
            "track": lesson.track,
            "difficulty": lesson.difficulty,
            "description": lesson.description,
            "key_concepts": lesson.key_concepts,
            "examples": lesson.examples,
        }

    def practice_exercise(
        self, exercise_type: str = "note_identification", difficulty: str = "beginner"
    ) -> dict:
        """
        Generate and display a practice exercise.

        Args:
            exercise_type: Type of exercise
            difficulty: beginner / intermediate / advanced

        Returns:
            Exercise data as a dict (with options and correct answer).
        """
        exercise = self.learning.practice(exercise_type, difficulty=difficulty)
        print(f"\n🎯 Exercise: {exercise.question}")
        for i, opt in enumerate(exercise.options, start=1):
            print(f"   {i}. {opt}")
        return {
            "id": exercise.id,
            "question": exercise.question,
            "options": exercise.options,
            "correct_answer": exercise.correct_answer,
            "explanation": exercise.explanation,
            "hints": exercise.hints,
        }

    def get_learning_score(self) -> dict:
        """Return the current learning session score."""
        score = self.learning.get_score()
        print(f"\n📊 Learning Score: {score['correct']}/{score['total']} "
              f"({score['accuracy']}%)")
        return score

    def _print_system_status(self) -> None:
        """Print system status."""
        status = self.orchestrator.get_system_info()
        print("\n📊 System Status:")
        print(f"   Modules: {', '.join(status['modules'])}")
        print(f"   Sample Rate: {self.sample_rate} Hz")

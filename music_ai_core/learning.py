"""
Learning Module – Interactive Music Theory Learning Engine

Provides:
- Lesson registry covering the five core learning tracks:
    1. Elements  (notes, intervals, scales)
    2. Chords    (triads, seventh, extensions)
    3. Rhythm    (meter, subdivision, groove)
    4. Melody    (contour, phrase, motive)
    5. Harmony   (functional harmony, voice leading, modulation)
- Exercise generator (multiple choice, identification, listening)
- Progress tracker (per-student session)
- Difficulty levels: beginner, intermediate, advanced
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from music_ai_core.elements import (
    ALL_NOTE_NAMES,
    SCALE_PATTERNS,
    CHORD_INTERVALS,
    RHYTHM_PATTERNS,
    get_scale,
    get_chord,
    interval_name,
    list_scales,
    list_chords,
    list_rhythms,
)


# ---------------------------------------------------------------------------
# Difficulty levels
# ---------------------------------------------------------------------------

DIFFICULTY_LEVELS = ["beginner", "intermediate", "advanced"]


# ---------------------------------------------------------------------------
# Lesson data
# ---------------------------------------------------------------------------

@dataclass
class Lesson:
    """A single music theory lesson."""
    id: str
    title: str
    track: str           # One of: elements, chords, rhythm, melody, harmony
    difficulty: str      # beginner / intermediate / advanced
    description: str
    key_concepts: List[str]
    examples: List[str]
    exercise_types: List[str]


LESSONS: Dict[str, Lesson] = {
    # ----- Elements track -----------------------------------------------
    "el_01": Lesson(
        id="el_01",
        title="The Musical Alphabet",
        track="elements",
        difficulty="beginner",
        description=(
            "Learn the 12 notes of Western music, their names, and how they "
            "relate to each other on a piano keyboard or guitar fretboard."
        ),
        key_concepts=["12-tone chromatic scale", "sharp (#) and flat (b)", "enharmonic equivalents"],
        examples=["C, C#/Db, D, D#/Eb, E, F, F#/Gb, G, G#/Ab, A, A#/Bb, B"],
        exercise_types=["note_identification", "note_naming"],
    ),
    "el_02": Lesson(
        id="el_02",
        title="Intervals",
        track="elements",
        difficulty="beginner",
        description=(
            "Understand intervals – the distance in pitch between two notes. "
            "Intervals are the building blocks of melody and harmony."
        ),
        key_concepts=[
            "semitone (half step)", "tone (whole step)", "naming intervals (minor 2nd … octave)",
        ],
        examples=["C → D = Major 2nd (2 semitones)", "C → G = Perfect 5th (7 semitones)"],
        exercise_types=["interval_identification", "interval_building"],
    ),
    "el_03": Lesson(
        id="el_03",
        title="Major & Minor Scales",
        track="elements",
        difficulty="beginner",
        description=(
            "Build major and minor scales from any root note using whole- and "
            "half-step patterns."
        ),
        key_concepts=["W-W-H-W-W-W-H pattern (major)", "W-H-W-W-H-W-W (natural minor)"],
        examples=["C major: C D E F G A B C", "A minor: A B C D E F G A"],
        exercise_types=["scale_building", "scale_identification"],
    ),
    "el_04": Lesson(
        id="el_04",
        title="Pentatonic & Blues Scales",
        track="elements",
        difficulty="intermediate",
        description="Learn the five-note pentatonic and six-note blues scales used in pop, rock, and jazz.",
        key_concepts=["pentatonic major", "pentatonic minor", "blues scale / blue note"],
        examples=["A pentatonic minor: A C D E G", "A blues: A C D D# E G"],
        exercise_types=["scale_building", "genre_matching"],
    ),
    # ----- Chords track -------------------------------------------------
    "ch_01": Lesson(
        id="ch_01",
        title="Major & Minor Triads",
        track="chords",
        difficulty="beginner",
        description="A triad is a three-note chord built by stacking thirds. Master major and minor triads.",
        key_concepts=["root, third, fifth", "major triad (4+3 semitones)", "minor triad (3+4 semitones)"],
        examples=["C major: C E G", "A minor: A C E"],
        exercise_types=["chord_identification", "chord_building"],
    ),
    "ch_02": Lesson(
        id="ch_02",
        title="Seventh Chords",
        track="chords",
        difficulty="intermediate",
        description="Extend triads to four notes by adding a seventh. Covers major7, dominant7, minor7.",
        key_concepts=["major 7th", "dominant 7th", "minor 7th", "half-diminished 7th"],
        examples=["Cmaj7: C E G B", "G7: G B D F"],
        exercise_types=["chord_identification", "chord_building", "chord_progression"],
    ),
    "ch_03": Lesson(
        id="ch_03",
        title="Chord Progressions",
        track="chords",
        difficulty="intermediate",
        description=(
            "Combine chords into progressions. Explore the I-IV-V, ii-V-I, "
            "and I-V-vi-IV progressions that power most popular music."
        ),
        key_concepts=["Roman numeral analysis", "tonic / subdominant / dominant function",
                      "I-IV-V", "ii-V-I", "I-V-vi-IV"],
        examples=["I-IV-V in C: C F G", "I-V-vi-IV in C: C G Am F"],
        exercise_types=["progression_completion", "key_identification"],
    ),
    # ----- Rhythm track -------------------------------------------------
    "rh_01": Lesson(
        id="rh_01",
        title="Meter & Time Signatures",
        track="rhythm",
        difficulty="beginner",
        description="Understand how music is organised into recurring beat groups via time signatures.",
        key_concepts=["beat", "measure/bar", "4/4 common time", "3/4 waltz", "6/8 compound"],
        examples=["4/4: 4 quarter-note beats per bar", "3/4: 3 quarter-note beats (waltz)"],
        exercise_types=["meter_identification", "clapping_exercise"],
    ),
    "rh_02": Lesson(
        id="rh_02",
        title="Note Values & Rests",
        track="rhythm",
        difficulty="beginner",
        description="Learn whole, half, quarter, eighth, and sixteenth notes and their corresponding rests.",
        key_concepts=["whole note (4 beats)", "half note (2 beats)", "quarter note (1 beat)",
                      "eighth note (½ beat)", "dotted values"],
        examples=["Quarter + dotted eighth + sixteenth = 2 beats"],
        exercise_types=["note_value_identification", "rhythm_completion"],
    ),
    "rh_03": Lesson(
        id="rh_03",
        title="Syncopation & Groove",
        track="rhythm",
        difficulty="intermediate",
        description="Explore off-beat accents, swing, and groove – the rhythmic feel that makes music move.",
        key_concepts=["syncopation", "swing (shuffle)", "the 'pocket'", "ghost notes"],
        examples=["Reggae skank: accent on beats 2 and 4"],
        exercise_types=["rhythm_identification", "groove_matching"],
    ),
    # ----- Melody track -------------------------------------------------
    "me_01": Lesson(
        id="me_01",
        title="Melodic Contour",
        track="melody",
        difficulty="beginner",
        description="Understand how a melody's shape (contour) creates emotional direction and interest.",
        key_concepts=["stepwise motion", "leaps", "climax note", "arch shape", "descending resolution"],
        examples=["Ascending lines create tension; descending lines provide resolution"],
        exercise_types=["contour_identification", "melody_completion"],
    ),
    "me_02": Lesson(
        id="me_02",
        title="Phrase & Motive",
        track="melody",
        difficulty="intermediate",
        description="Learn how short motives grow into phrases and how phrases create musical sentences.",
        key_concepts=["motive", "phrase", "antecedent / consequent", "sequence"],
        examples=["Beethoven's 5th opening motive: G G G Eb (repeated, varied)"],
        exercise_types=["phrase_identification", "motive_development"],
    ),
    # ----- Harmony track ------------------------------------------------
    "ha_01": Lesson(
        id="ha_01",
        title="Diatonic Harmony",
        track="harmony",
        difficulty="intermediate",
        description="Build chords from every degree of a scale to create a key's harmonic palette.",
        key_concepts=["diatonic chords", "scale degrees I–VII", "tonic / predominant / dominant"],
        examples=["C major diatonic: C Dm Em F G Am Bdim"],
        exercise_types=["chord_function_identification", "progression_analysis"],
    ),
    "ha_02": Lesson(
        id="ha_02",
        title="Modulation & Key Change",
        track="harmony",
        difficulty="advanced",
        description="Discover how composers move between keys for variety and dramatic effect.",
        key_concepts=["pivot chord", "direct modulation", "secondary dominant", "common-tone modulation"],
        examples=["C major → G major via V/V (D7)"],
        exercise_types=["key_identification", "modulation_detection"],
    ),
}


# ---------------------------------------------------------------------------
# Exercise generator
# ---------------------------------------------------------------------------

@dataclass
class Exercise:
    """A single learner exercise."""
    id: str
    exercise_type: str
    question: str
    options: List[str]          # Multiple-choice options ([] if open-ended)
    correct_answer: str
    explanation: str
    difficulty: str
    track: str
    hints: List[str] = field(default_factory=list)


class ExerciseGenerator:
    """Generate music theory exercises dynamically."""

    def __init__(self, seed: Optional[int] = None):
        self._rng = random.Random(seed)

    def generate(
        self,
        exercise_type: str,
        difficulty: str = "beginner",
        track: Optional[str] = None,
    ) -> Exercise:
        """
        Generate a single exercise.

        Args:
            exercise_type: Type of exercise (see ``EXERCISE_TYPE_MAP``)
            difficulty: ``"beginner"``, ``"intermediate"``, or ``"advanced"``
            track: Optional learning track filter

        Returns:
            An :class:`Exercise` instance.
        """
        dispatch = {
            "note_identification":   self._note_identification,
            "interval_identification": self._interval_identification,
            "scale_building":        self._scale_building,
            "chord_building":        self._chord_building,
            "chord_identification":  self._chord_identification,
            "meter_identification":  self._meter_identification,
            "note_value_identification": self._note_value_identification,
        }
        if exercise_type not in dispatch:
            # Fall back to note identification for unknown types
            exercise_type = "note_identification"

        return dispatch[exercise_type](difficulty)

    # ------------------------------------------------------------------
    # Individual exercise generators
    # ------------------------------------------------------------------

    def _note_identification(self, difficulty: str) -> Exercise:
        note = self._rng.choice(ALL_NOTE_NAMES)
        distractors = self._rng.sample([n for n in ALL_NOTE_NAMES if n != note], k=3)
        options = sorted([note] + distractors, key=lambda _: self._rng.random())
        return Exercise(
            id=f"note_id_{note}",
            exercise_type="note_identification",
            question=f"Which note sits between G# and A# on the chromatic scale?",
            options=options,
            correct_answer=note,
            explanation=f"The note '{note}' is part of the 12-note chromatic scale.",
            difficulty=difficulty,
            track="elements",
        )

    def _interval_identification(self, difficulty: str) -> Exercise:
        note_a = self._rng.choice(ALL_NOTE_NAMES[:8])
        semitones = self._rng.randint(1, 11)
        note_b_idx = (ALL_NOTE_NAMES.index(note_a) + semitones) % 12
        note_b = ALL_NOTE_NAMES[note_b_idx]
        correct = interval_name(semitones)

        from music_ai_core.elements import INTERVAL_SEMITONES
        all_intervals = list(INTERVAL_SEMITONES.keys())
        distractors = self._rng.sample(
            [i for i in all_intervals if i != correct], k=min(3, len(all_intervals) - 1)
        )
        options = [correct] + distractors
        self._rng.shuffle(options)

        return Exercise(
            id=f"interval_{note_a}_{note_b}",
            exercise_type="interval_identification",
            question=f"What interval is from {note_a} up to {note_b}?",
            options=options,
            correct_answer=correct,
            explanation=f"{note_a} to {note_b} is {semitones} semitone(s) = {correct}.",
            difficulty=difficulty,
            track="elements",
            hints=[f"Count the semitones: {semitones}"],
        )

    def _scale_building(self, difficulty: str) -> Exercise:
        root = self._rng.choice(["C", "D", "E", "F", "G", "A", "B"])
        if difficulty == "beginner":
            scale_type = self._rng.choice(["major", "minor"])
        else:
            scale_type = self._rng.choice(list(SCALE_PATTERNS.keys()))

        notes = get_scale(root, scale_type, octave=4)
        note_names = [key.rstrip("01234567890") for key, _ in notes]
        correct = " ".join(note_names)

        # Generate wrong answers by using a different scale type
        wrong_types = [s for s in ["major", "minor", "pentatonic_minor"] if s != scale_type]
        wrongs = []
        for wt in wrong_types[:2]:
            wn = get_scale(root, wt, octave=4)
            wrongs.append(" ".join(k.rstrip("01234567890") for k, _ in wn))
        # Add one completely shuffled distractor
        shuffled = note_names[:]
        self._rng.shuffle(shuffled)
        wrongs.append(" ".join(shuffled))

        options = [correct] + wrongs[:3]
        self._rng.shuffle(options)

        return Exercise(
            id=f"scale_{root}_{scale_type}",
            exercise_type="scale_building",
            question=f"Which sequence of notes makes up the {root} {scale_type} scale?",
            options=options,
            correct_answer=correct,
            explanation=f"{root} {scale_type}: {correct}",
            difficulty=difficulty,
            track="elements",
        )

    def _chord_building(self, difficulty: str) -> Exercise:
        root = self._rng.choice(["C", "D", "E", "F", "G", "A", "B"])
        if difficulty == "beginner":
            chord_type = self._rng.choice(["major", "minor"])
        else:
            chord_type = self._rng.choice(
                ["major", "minor", "dominant7", "major7", "minor7"]
            )

        chord_notes = get_chord(root, chord_type, octave=4)
        note_names = [k.rstrip("01234567890") for k, _ in chord_notes]
        correct = " ".join(note_names)

        wrong_types = [c for c in ["major", "minor", "diminished"] if c != chord_type]
        wrongs = []
        for wt in wrong_types[:2]:
            wn = get_chord(root, wt, octave=4)
            wrongs.append(" ".join(k.rstrip("01234567890") for k, _ in wn))
        shuffled = note_names[:]
        self._rng.shuffle(shuffled)
        wrongs.append(" ".join(shuffled))

        options = [correct] + wrongs[:3]
        self._rng.shuffle(options)

        return Exercise(
            id=f"chord_{root}_{chord_type}",
            exercise_type="chord_building",
            question=f"Which notes form a {root} {chord_type} chord?",
            options=options,
            correct_answer=correct,
            explanation=f"{root} {chord_type}: {correct}",
            difficulty=difficulty,
            track="chords",
        )

    def _chord_identification(self, difficulty: str) -> Exercise:
        root = self._rng.choice(["C", "D", "F", "G", "A"])
        chord_type = self._rng.choice(["major", "minor", "diminished", "augmented"])
        chord_notes = get_chord(root, chord_type, octave=4)
        note_names = " ".join(k.rstrip("01234567890") for k, _ in chord_notes)
        correct = f"{root} {chord_type}"

        all_types = ["major", "minor", "diminished", "augmented"]
        wrong_types = [t for t in all_types if t != chord_type]
        distractors = [f"{root} {t}" for t in self._rng.sample(wrong_types, k=3)]
        options = [correct] + distractors
        self._rng.shuffle(options)

        return Exercise(
            id=f"chord_id_{root}_{chord_type}",
            exercise_type="chord_identification",
            question=f"The notes {note_names} form which chord?",
            options=options,
            correct_answer=correct,
            explanation=f"{note_names} = {correct}",
            difficulty=difficulty,
            track="chords",
        )

    def _meter_identification(self, difficulty: str) -> Exercise:
        meters = {
            "4/4": "4 quarter beats per bar – the most common time signature in pop and rock",
            "3/4": "3 quarter beats per bar – waltz feel",
            "6/8": "6 eighth beats per bar – compound duple, feels like 2 with a swing",
            "5/4": "5 quarter beats per bar – asymmetric, used in jazz and progressive music",
        }
        correct, explanation = self._rng.choice(list(meters.items()))
        options = list(meters.keys())
        self._rng.shuffle(options)
        return Exercise(
            id=f"meter_{correct.replace('/', '_')}",
            exercise_type="meter_identification",
            question=f"A piece feels like a strong ONE-two-three-ONE-two-three pattern. "
                     f"Which time signature is it most likely in?",
            options=options,
            correct_answer=correct,
            explanation=meters[correct],
            difficulty=difficulty,
            track="rhythm",
        )

    def _note_value_identification(self, difficulty: str) -> Exercise:
        values = {
            "whole note":     "4 beats in 4/4 time",
            "half note":      "2 beats in 4/4 time",
            "quarter note":   "1 beat in 4/4 time",
            "eighth note":    "½ beat (0.5) in 4/4 time",
            "sixteenth note": "¼ beat (0.25) in 4/4 time",
        }
        correct, explanation = self._rng.choice(list(values.items()))
        options = list(values.keys())
        self._rng.shuffle(options)
        return Exercise(
            id=f"note_value_{correct.replace(' ', '_')}",
            exercise_type="note_value_identification",
            question=f"Which note value lasts {values[correct]}?",
            options=options,
            correct_answer=correct,
            explanation=explanation,
            difficulty=difficulty,
            track="rhythm",
        )


# ---------------------------------------------------------------------------
# Progress tracker
# ---------------------------------------------------------------------------

@dataclass
class StudentProgress:
    """Tracks a learner's progress through lessons and exercises."""
    student_id: str
    completed_lessons: List[str] = field(default_factory=list)
    exercise_results: List[Dict[str, Any]] = field(default_factory=list)
    current_track: str = "elements"
    current_difficulty: str = "beginner"

    def record_result(self, exercise: Exercise, answer: str) -> bool:
        """
        Record the result of an exercise attempt.

        Args:
            exercise: The exercise that was attempted
            answer: The student's answer

        Returns:
            ``True`` if the answer is correct, ``False`` otherwise.
        """
        correct = answer.strip().lower() == exercise.correct_answer.strip().lower()
        self.exercise_results.append({
            "exercise_id": exercise.id,
            "track": exercise.track,
            "difficulty": exercise.difficulty,
            "correct": correct,
            "student_answer": answer,
            "correct_answer": exercise.correct_answer,
        })
        return correct

    def complete_lesson(self, lesson_id: str) -> None:
        """Mark a lesson as completed."""
        if lesson_id not in self.completed_lessons:
            self.completed_lessons.append(lesson_id)

    def score(self) -> Dict[str, Any]:
        """Return overall and per-track accuracy statistics."""
        if not self.exercise_results:
            return {"total": 0, "correct": 0, "accuracy": 0.0, "by_track": {}}

        by_track: Dict[str, Dict[str, int]] = {}
        total_correct = 0
        for result in self.exercise_results:
            track = result["track"]
            if track not in by_track:
                by_track[track] = {"total": 0, "correct": 0}
            by_track[track]["total"] += 1
            if result["correct"]:
                by_track[track]["correct"] += 1
                total_correct += 1

        track_accuracy = {
            t: round(v["correct"] / v["total"] * 100, 1)
            for t, v in by_track.items()
        }

        return {
            "total": len(self.exercise_results),
            "correct": total_correct,
            "accuracy": round(total_correct / len(self.exercise_results) * 100, 1),
            "by_track": track_accuracy,
        }

    def suggest_next_lesson(self) -> Optional[str]:
        """Suggest the next lesson based on completed lessons and current track."""
        track_lessons = [
            lid for lid, lesson in LESSONS.items()
            if lesson.track == self.current_track
            and lid not in self.completed_lessons
            and lesson.difficulty == self.current_difficulty
        ]
        if track_lessons:
            return track_lessons[0]

        # Try advancing difficulty
        if self.current_difficulty == "beginner":
            self.current_difficulty = "intermediate"
        elif self.current_difficulty == "intermediate":
            self.current_difficulty = "advanced"
        else:
            self.current_difficulty = "beginner"
            # Move to next track
            tracks = ["elements", "chords", "rhythm", "melody", "harmony"]
            idx = tracks.index(self.current_track) if self.current_track in tracks else 0
            self.current_track = tracks[(idx + 1) % len(tracks)]

        # Try again
        track_lessons = [
            lid for lid, lesson in LESSONS.items()
            if lesson.track == self.current_track
            and lid not in self.completed_lessons
        ]
        return track_lessons[0] if track_lessons else None


# ---------------------------------------------------------------------------
# Learning session
# ---------------------------------------------------------------------------

class LearningSession:
    """
    Orchestrates a learner session: select lessons, run exercises, track progress.
    """

    def __init__(self, student_id: str = "default", seed: Optional[int] = None):
        self.progress = StudentProgress(student_id=student_id)
        self.exercise_gen = ExerciseGenerator(seed=seed)

    def start_lesson(self, lesson_id: str) -> Lesson:
        """Retrieve and display lesson content."""
        if lesson_id not in LESSONS:
            raise ValueError(f"Unknown lesson '{lesson_id}'. Available: {list(LESSONS.keys())}")
        lesson = LESSONS[lesson_id]
        self.progress.current_track = lesson.track
        self.progress.current_difficulty = lesson.difficulty
        return lesson

    def practice(
        self,
        exercise_type: str,
        difficulty: Optional[str] = None,
    ) -> Exercise:
        """Generate a practice exercise."""
        diff = difficulty or self.progress.current_difficulty
        return self.exercise_gen.generate(exercise_type, difficulty=diff)

    def answer(self, exercise: Exercise, answer: str) -> Dict[str, Any]:
        """
        Submit an answer to an exercise.

        Returns:
            Dict with ``correct``, ``feedback``, and ``explanation`` keys.
        """
        correct = self.progress.record_result(exercise, answer)
        return {
            "correct": correct,
            "feedback": "✅ Correct!" if correct else "❌ Not quite.",
            "explanation": exercise.explanation,
            "hints": exercise.hints if not correct else [],
        }

    def get_score(self) -> Dict[str, Any]:
        """Return the student's current score."""
        return self.progress.score()

    def next_lesson(self) -> Optional[Lesson]:
        """Return the next recommended lesson."""
        lesson_id = self.progress.suggest_next_lesson()
        if lesson_id:
            return self.start_lesson(lesson_id)
        return None


# ---------------------------------------------------------------------------
# Convenience helpers
# ---------------------------------------------------------------------------

def list_lessons(track: Optional[str] = None, difficulty: Optional[str] = None) -> List[str]:
    """Return lesson IDs filtered by track and/or difficulty."""
    return [
        lid for lid, lesson in LESSONS.items()
        if (track is None or lesson.track == track)
        and (difficulty is None or lesson.difficulty == difficulty)
    ]


def list_exercise_types() -> List[str]:
    """Return all available exercise type names."""
    return [
        "note_identification",
        "interval_identification",
        "scale_building",
        "chord_building",
        "chord_identification",
        "meter_identification",
        "note_value_identification",
    ]

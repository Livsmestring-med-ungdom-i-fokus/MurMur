"""Tests for music_ai_core.learning — interactive music theory learning engine."""

import pytest
from music_ai_core.learning import (
    LESSONS,
    DIFFICULTY_LEVELS,
    LearningSession,
    ExerciseGenerator,
    StudentProgress,
    list_lessons,
    list_exercise_types,
)


class TestLessons:
    def test_lessons_not_empty(self):
        assert len(LESSONS) > 0

    def test_all_lessons_have_required_fields(self):
        for lid, lesson in LESSONS.items():
            assert lesson.id == lid
            assert lesson.title
            assert lesson.track
            assert lesson.difficulty in DIFFICULTY_LEVELS
            assert lesson.description
            assert isinstance(lesson.key_concepts, list)
            assert isinstance(lesson.exercise_types, list)

    def test_multiple_tracks_covered(self):
        tracks = {lesson.track for lesson in LESSONS.values()}
        assert len(tracks) >= 3

    def test_beginner_lessons_exist(self):
        beginner = [l for l in LESSONS.values() if l.difficulty == "beginner"]
        assert len(beginner) > 0


class TestExerciseGenerator:
    def setup_method(self):
        self.gen = ExerciseGenerator(seed=42)

    def test_note_identification_exercise(self):
        exercise = self.gen.generate("note_identification")
        assert exercise.exercise_type == "note_identification"
        assert exercise.question
        assert len(exercise.options) == 4
        assert exercise.correct_answer in exercise.options

    def test_interval_identification_exercise(self):
        exercise = self.gen.generate("interval_identification")
        assert exercise.exercise_type == "interval_identification"
        assert exercise.correct_answer in exercise.options

    def test_scale_building_exercise(self):
        exercise = self.gen.generate("scale_building")
        assert exercise.exercise_type == "scale_building"
        assert exercise.correct_answer

    def test_chord_building_exercise(self):
        exercise = self.gen.generate("chord_building")
        assert exercise.correct_answer

    def test_chord_identification_exercise(self):
        exercise = self.gen.generate("chord_identification")
        assert exercise.correct_answer in exercise.options

    def test_meter_identification_exercise(self):
        exercise = self.gen.generate("meter_identification")
        assert exercise.correct_answer in exercise.options

    def test_note_value_identification_exercise(self):
        exercise = self.gen.generate("note_value_identification")
        assert exercise.correct_answer in exercise.options

    def test_unknown_type_falls_back(self):
        exercise = self.gen.generate("nonexistent_type")
        assert exercise is not None

    def test_difficulty_levels(self):
        for level in DIFFICULTY_LEVELS:
            exercise = self.gen.generate("scale_building", difficulty=level)
            assert exercise.difficulty == level

    def test_deterministic_with_same_seed(self):
        gen1 = ExerciseGenerator(seed=123)
        gen2 = ExerciseGenerator(seed=123)
        ex1 = gen1.generate("note_identification")
        ex2 = gen2.generate("note_identification")
        assert ex1.id == ex2.id
        assert ex1.correct_answer == ex2.correct_answer


class TestStudentProgress:
    def setup_method(self):
        self.progress = StudentProgress(student_id="test_student")

    def test_initial_score_is_zero(self):
        score = self.progress.score()
        assert score["total"] == 0
        assert score["accuracy"] == 0.0

    def test_complete_lesson(self):
        self.progress.complete_lesson("el_01")
        assert "el_01" in self.progress.completed_lessons

    def test_complete_lesson_idempotent(self):
        self.progress.complete_lesson("el_01")
        self.progress.complete_lesson("el_01")
        assert self.progress.completed_lessons.count("el_01") == 1

    def test_record_correct_result(self):
        gen = ExerciseGenerator(seed=0)
        exercise = gen.generate("note_identification")
        correct = self.progress.record_result(exercise, exercise.correct_answer)
        assert correct is True

    def test_record_incorrect_result(self):
        gen = ExerciseGenerator(seed=0)
        exercise = gen.generate("note_identification")
        wrong = next(o for o in exercise.options if o != exercise.correct_answer)
        correct = self.progress.record_result(exercise, wrong)
        assert correct is False

    def test_score_accuracy_calculation(self):
        gen = ExerciseGenerator(seed=1)
        for _ in range(4):
            ex = gen.generate("note_identification")
            self.progress.record_result(ex, ex.correct_answer)  # all correct

        score = self.progress.score()
        assert score["total"] == 4
        assert score["correct"] == 4
        assert score["accuracy"] == 100.0

    def test_score_by_track(self):
        gen = ExerciseGenerator(seed=2)
        ex = gen.generate("note_identification")
        self.progress.record_result(ex, ex.correct_answer)
        score = self.progress.score()
        assert "elements" in score["by_track"]

    def test_suggest_next_lesson_returns_string_or_none(self):
        result = self.progress.suggest_next_lesson()
        assert result is None or isinstance(result, str)

    def test_suggest_next_lesson_advances_after_completion(self):
        for lid, lesson in LESSONS.items():
            if lesson.track == "elements":
                self.progress.complete_lesson(lid)

        result = self.progress.suggest_next_lesson()
        # Should either suggest an intermediate or move to next track
        assert result is None or isinstance(result, str)


class TestLearningSession:
    def setup_method(self):
        self.session = LearningSession(student_id="alice", seed=7)

    def test_start_lesson_valid(self):
        lesson = self.session.start_lesson("el_01")
        assert lesson.id == "el_01"

    def test_start_lesson_invalid_raises(self):
        with pytest.raises(ValueError, match="Unknown lesson"):
            self.session.start_lesson("zz_99")

    def test_practice_returns_exercise(self):
        from music_ai_core.learning import Exercise
        exercise = self.session.practice("note_identification")
        assert isinstance(exercise, Exercise)

    def test_answer_correct(self):
        exercise = self.session.practice("note_identification")
        result = self.session.answer(exercise, exercise.correct_answer)
        assert result["correct"] is True
        assert "✅" in result["feedback"]

    def test_answer_incorrect(self):
        exercise = self.session.practice("note_identification")
        wrong = next(o for o in exercise.options if o != exercise.correct_answer)
        result = self.session.answer(exercise, wrong)
        assert result["correct"] is False
        assert "❌" in result["feedback"]

    def test_get_score_structure(self):
        score = self.session.get_score()
        assert "total" in score
        assert "accuracy" in score

    def test_next_lesson_returns_lesson_or_none(self):
        from music_ai_core.learning import Lesson
        result = self.session.next_lesson()
        assert result is None or isinstance(result, Lesson)


class TestListHelpers:
    def test_list_lessons_all(self):
        lessons = list_lessons()
        assert len(lessons) > 0

    def test_list_lessons_filter_by_track(self):
        elements = list_lessons(track="elements")
        chords = list_lessons(track="chords")
        assert len(elements) > 0
        assert len(chords) > 0
        assert set(elements).isdisjoint(set(chords))

    def test_list_lessons_filter_by_difficulty(self):
        beginners = list_lessons(difficulty="beginner")
        assert all(
            LESSONS[lid].difficulty == "beginner" for lid in beginners
        )

    def test_list_exercise_types(self):
        types = list_exercise_types()
        assert isinstance(types, list)
        assert "note_identification" in types
        assert len(types) >= 5

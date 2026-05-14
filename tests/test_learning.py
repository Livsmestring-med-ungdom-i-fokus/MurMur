"""Tests for music_ai_core.learning – lessons, exercises, and progress tracking."""

import pytest

from music_ai_core.learning import (
    LESSONS,
    Exercise,
    ExerciseGenerator,
    LearningSession,
    StudentProgress,
    list_lessons,
    list_exercise_types,
)


# ---------------------------------------------------------------------------
# LESSONS registry
# ---------------------------------------------------------------------------

class TestLessons:
    def test_lessons_non_empty(self):
        assert len(LESSONS) > 0

    def test_lesson_tracks(self):
        tracks = {lesson.track for lesson in LESSONS.values()}
        for expected in ("elements", "chords", "rhythm", "melody", "harmony"):
            assert expected in tracks

    def test_lesson_difficulties(self):
        difficulties = {lesson.difficulty for lesson in LESSONS.values()}
        assert "beginner" in difficulties
        assert "intermediate" in difficulties

    def test_lesson_ids_match_keys(self):
        for lid, lesson in LESSONS.items():
            assert lesson.id == lid

    def test_lesson_has_concepts(self):
        for lid, lesson in LESSONS.items():
            assert len(lesson.key_concepts) > 0, f"{lid} has no key_concepts"

    def test_lesson_has_exercise_types(self):
        for lid, lesson in LESSONS.items():
            assert len(lesson.exercise_types) > 0, f"{lid} has no exercise_types"


# ---------------------------------------------------------------------------
# list_lessons / list_exercise_types
# ---------------------------------------------------------------------------

class TestListHelpers:
    def test_list_lessons_all(self):
        all_lessons = list_lessons()
        assert len(all_lessons) == len(LESSONS)

    def test_list_lessons_filter_track(self):
        elements = list_lessons(track="elements")
        assert all(LESSONS[lid].track == "elements" for lid in elements)
        assert len(elements) > 0

    def test_list_lessons_filter_difficulty(self):
        beginners = list_lessons(difficulty="beginner")
        assert all(LESSONS[lid].difficulty == "beginner" for lid in beginners)
        assert len(beginners) > 0

    def test_list_lessons_filter_both(self):
        result = list_lessons(track="chords", difficulty="intermediate")
        for lid in result:
            assert LESSONS[lid].track == "chords"
            assert LESSONS[lid].difficulty == "intermediate"

    def test_list_exercise_types_non_empty(self):
        types = list_exercise_types()
        assert len(types) > 0
        assert "note_identification" in types
        assert "chord_building" in types


# ---------------------------------------------------------------------------
# ExerciseGenerator
# ---------------------------------------------------------------------------

class TestExerciseGenerator:
    @pytest.fixture
    def gen(self):
        return ExerciseGenerator(seed=42)

    EXERCISE_TYPES = [
        "note_identification",
        "interval_identification",
        "scale_building",
        "chord_building",
        "chord_identification",
        "meter_identification",
        "note_value_identification",
    ]

    @pytest.mark.parametrize("ex_type", EXERCISE_TYPES)
    def test_generate_returns_exercise(self, gen, ex_type):
        ex = gen.generate(ex_type)
        assert isinstance(ex, Exercise)

    @pytest.mark.parametrize("ex_type", EXERCISE_TYPES)
    def test_correct_answer_in_options(self, gen, ex_type):
        ex = gen.generate(ex_type)
        if ex.options:
            assert ex.correct_answer in ex.options, (
                f"{ex_type}: correct_answer '{ex.correct_answer}' not in options {ex.options}"
            )

    def test_unknown_type_falls_back(self, gen):
        ex = gen.generate("nonexistent_type")
        assert ex.exercise_type == "note_identification"

    def test_difficulty_labels_preserved(self, gen):
        for diff in ("beginner", "intermediate", "advanced"):
            ex = gen.generate("scale_building", difficulty=diff)
            assert ex.difficulty == diff

    def test_seed_reproducibility(self):
        a = ExerciseGenerator(seed=99).generate("note_identification")
        b = ExerciseGenerator(seed=99).generate("note_identification")
        assert a.correct_answer == b.correct_answer


# ---------------------------------------------------------------------------
# StudentProgress
# ---------------------------------------------------------------------------

class TestStudentProgress:
    @pytest.fixture
    def progress(self):
        return StudentProgress(student_id="test_student")

    def test_initial_score_zeros(self, progress):
        score = progress.score()
        assert score["total"] == 0
        assert score["correct"] == 0
        assert score["accuracy"] == 0.0

    def test_record_correct_answer(self, progress):
        gen = ExerciseGenerator(seed=1)
        ex = gen.generate("note_identification")
        result = progress.record_result(ex, ex.correct_answer)
        assert result is True
        assert progress.score()["correct"] == 1

    def test_record_wrong_answer(self, progress):
        gen = ExerciseGenerator(seed=1)
        ex = gen.generate("note_identification")
        wrong = "not_a_real_note_xyz"
        result = progress.record_result(ex, wrong)
        assert result is False
        assert progress.score()["correct"] == 0

    def test_score_accuracy(self, progress):
        gen = ExerciseGenerator(seed=5)
        ex = gen.generate("note_identification")
        progress.record_result(ex, ex.correct_answer)  # correct
        progress.record_result(ex, "wrong")             # incorrect
        score = progress.score()
        assert score["total"] == 2
        assert score["correct"] == 1
        assert score["accuracy"] == pytest.approx(50.0)

    def test_complete_lesson(self, progress):
        progress.complete_lesson("el_01")
        assert "el_01" in progress.completed_lessons

    def test_complete_lesson_idempotent(self, progress):
        progress.complete_lesson("el_01")
        progress.complete_lesson("el_01")
        assert progress.completed_lessons.count("el_01") == 1

    def test_suggest_next_lesson_returns_string_or_none(self, progress):
        suggestion = progress.suggest_next_lesson()
        assert suggestion is None or isinstance(suggestion, str)

    def test_suggest_next_lesson_respects_completed(self, progress):
        first = progress.suggest_next_lesson()
        if first:
            progress.complete_lesson(first)
            second = progress.suggest_next_lesson()
            assert second != first or second is None

    def test_score_by_track(self, progress):
        gen = ExerciseGenerator(seed=10)
        ex = gen.generate("chord_building")
        progress.record_result(ex, ex.correct_answer)
        score = progress.score()
        assert "chords" in score["by_track"]


# ---------------------------------------------------------------------------
# LearningSession
# ---------------------------------------------------------------------------

class TestLearningSession:
    @pytest.fixture
    def session(self):
        return LearningSession(student_id="learner", seed=42)

    def test_start_lesson_returns_lesson(self, session):
        lesson = session.start_lesson("el_01")
        from music_ai_core.learning import Lesson
        assert isinstance(lesson, Lesson)
        assert lesson.id == "el_01"

    def test_start_lesson_updates_track(self, session):
        session.start_lesson("el_01")
        assert session.progress.current_track == "elements"

    def test_start_lesson_invalid_raises(self, session):
        with pytest.raises(ValueError, match="Unknown lesson"):
            session.start_lesson("zz_99")

    def test_practice_returns_exercise(self, session):
        ex = session.practice("note_identification")
        assert isinstance(ex, Exercise)

    def test_answer_correct(self, session):
        ex = session.practice("note_identification")
        feedback = session.answer(ex, ex.correct_answer)
        assert feedback["correct"] is True
        assert "explanation" in feedback

    def test_answer_incorrect(self, session):
        ex = session.practice("note_identification")
        feedback = session.answer(ex, "__wrong__")
        assert feedback["correct"] is False
        assert len(feedback["hints"]) > 0 or feedback["hints"] == []

    def test_get_score_after_answer(self, session):
        ex = session.practice("note_identification")
        session.answer(ex, ex.correct_answer)
        score = session.get_score()
        assert score["total"] == 1

    def test_next_lesson(self, session):
        session.start_lesson("el_01")
        session.progress.complete_lesson("el_01")
        lesson = session.next_lesson()
        assert lesson is None or lesson.id != "el_01"

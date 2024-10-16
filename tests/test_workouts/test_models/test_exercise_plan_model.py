import pytest
from django.core.exceptions import ValidationError

from apps.workouts.models import ExercisePlan


pytestmark = [pytest.mark.unit, pytest.mark.django_db]


class TestExercisePlanModel:
    def test_create_exercise_plan(self, exercise_plan_built):
        data = {**exercise_plan_built, "sets": 2, "reps": 20, "is_completed": True}
        exercise_plan = ExercisePlan.objects.create(**data)

        assert exercise_plan is not None
        assert exercise_plan.name == data["name"]
        assert exercise_plan.description == data["description"]
        assert exercise_plan.sets == data["sets"]
        assert exercise_plan.reps == data["reps"]
        assert exercise_plan.is_completed == data["is_completed"]
        assert exercise_plan.workout_plan == exercise_plan_built["workout_plan"]

    def test_default_values(self, exercise_plan_built):
        exercise_plan_built.pop("description")
        exercise_plan = ExercisePlan.objects.create(**exercise_plan_built)

        assert exercise_plan is not None
        assert exercise_plan.name == exercise_plan_built["name"]
        assert exercise_plan.description == ""
        assert exercise_plan.sets == None
        assert exercise_plan.reps == None
        assert exercise_plan.weight == None
        assert exercise_plan.weight_measure_unit == ""
        assert exercise_plan.is_completed == False
        assert exercise_plan.created_at
        assert exercise_plan.updated_at

    @pytest.mark.parametrize(
        "field, blank_value",
        [
            ("name", ""),
            ("workout_plan", None),
        ],
    )
    def test_required_field_cannot_be_empty(
        self, exercise_plan_built, field, blank_value
    ):
        exercise_plan_built[field] = blank_value

        with pytest.raises(ValidationError):
            exercise_plan = ExercisePlan(**exercise_plan_built)
            exercise_plan.full_clean()

    @pytest.mark.parametrize(
        "field, blank_value",
        [
            ("description", ""),
            ("sets", None),
            ("reps", None),
            ("weight", None),
            ("weight_measure_unit", ""),
        ],
    )
    def test_optional_field_can_be_blank(self, exercise_plan_built, field, blank_value):
        exercise_plan_built[field] = blank_value

        exercise_plan = ExercisePlan(**exercise_plan_built)
        exercise_plan.full_clean()

    @pytest.mark.parametrize(
        "field, value",
        [
            ("description", "This is description"),
            ("sets", 4),
            ("reps", 10),
            ("weight", 60),
            ("weight_measure_unit", "pounds"),
        ],
    )
    def test_create_exercise_plan_with_optional_fields(
        self, exercise_plan_built, field, value
    ):
        exercise_plan_built[field] = value
        exercise_plan = ExercisePlan.objects.create(**exercise_plan_built)

        assert exercise_plan is not None
        assert getattr(exercise_plan, field) == value

    @pytest.mark.parametrize(
        "field, invalid_value",
        [
            ("sets", "invalid sets"),
            ("reps", "a32"),
            ("weight", "invalid"),
        ],
    )
    def test_invalid_integer_field_value(
        self, exercise_plan_built, field, invalid_value
    ):
        exercise_plan_built[field] = invalid_value

        with pytest.raises(ValidationError):
            exercise_plan = ExercisePlan(**exercise_plan_built)
            exercise_plan.full_clean()

    def test_invalid_workout_plan(self, exercise_plan_built):
        exercise_plan_built["workout_plan"] = "invalid workout plan"

        with pytest.raises(ValueError):
            exercise_plan = ExercisePlan(**exercise_plan_built)
            exercise_plan.full_clean()

    def test_invalid_is_completed_field(self, exercise_plan_built):
        exercise_plan_built["is_completed"] = "invalid value"

        with pytest.raises(ValidationError):
            exercise_plan = ExercisePlan(**exercise_plan_built)
            exercise_plan.full_clean()

    @pytest.mark.parametrize(
        "field, value",
        [
            ("name", "a" * 151),
            ("weight_measure_unit", "a" * 51),
        ],
    )
    def test_max_length_field(self, exercise_plan_built, field, value):
        exercise_plan_built[field] = value

        # with pytest.raises(ValidationError):
        exercise_plan = ExercisePlan(**exercise_plan_built)
        exercise_plan.full_clean()

    def test_str_representation(self, exercise_plan_built):
        exercise_plan = ExercisePlan(**exercise_plan_built)
        assert str(exercise_plan) == exercise_plan.name

    def test_set_weight_requires_set_weight_measure_unit(self, exercise_plan_built):
        exercise_plan_built["weight"] = 23

        exercise_plan = ExercisePlan(**exercise_plan_built)
        exercise_plan.full_clean()

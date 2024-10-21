import pytest

from workouts.models import ExercisePlan


pytestmark = [pytest.mark.unit, pytest.mark.django_db]


class TestExercisePlanModel:
    def test_create_plan_with_required_field(self, exercise_created, workout_created):
        plan_data = {
            "name": "Test Exercise Plan",
            "exercise": exercise_created,
            "workout": workout_created,
        }

        plan = ExercisePlan.objects.create(**plan_data)

        assert plan.id is not None
        assert all([getattr(plan, field) == plan_data[field] for field in plan_data])

    def test_exercise_plan_str(self, exercise_created, workout_created):
        plan_data = {
            "name": "Test Exercise Plan",
            "exercise": exercise_created,
            "workout": workout_created,
        }

        plan = ExercisePlan(**plan_data)

        assert str(plan) == f"{plan.name} - {plan.exercise.name} ({plan.workout.name})"

    def test_create_default_values(self, exercise_created, workout_created):
        plan_data = {
            "name": "Test Exercise Plan",
            "exercise": exercise_created,
            "workout": workout_created,
        }
        plan = ExercisePlan.objects.create(**plan_data)

        assert plan.description == ""
        assert plan.sets is None
        assert plan.reps is None
        assert plan.weight is None
        assert plan.weight_measure_unit == ""
        assert plan.created_at is not None
        assert plan.updated_at is not None

    @pytest.mark.parametrize(
        "optional_field, value",
        [
            ("description", "This is a description"),
            ("sets", 10),
            ("reps", 20),
            ("weight", 60),
            ("weight_measure_unit", "pounds"),
        ],
    )
    def test_create_with_optional_fields(
        self, exercise_created, workout_created, optional_field, value
    ):
        plan_data = {
            "name": "Test Exercise Plan",
            "exercise": exercise_created,
            "workout": workout_created,
        }
        plan_data[optional_field] = value
        plan = ExercisePlan.objects.create(**plan_data)

        assert getattr(plan, optional_field) == value

    def test_workout_relationship(self, exercise_created, workout_created):
        plan_data = {
            "name": "Test Exercise Plan",
            "exercise": exercise_created,
            "workout": workout_created,
        }
        plan = ExercisePlan.objects.create(**plan_data)

        assert workout_created.exercise_plans.count() == 1
        assert workout_created.exercise_plans.first() == plan

    def test_workout_delete_cascade(self, exercise_created, workout_created):
        plan_data = {
            "name": "Test Exercise Plan",
            "exercise": exercise_created,
            "workout": workout_created,
        }
        ExercisePlan.objects.create(**plan_data)

        assert ExercisePlan.objects.count() == 1
        workout_created.delete()

        assert ExercisePlan.objects.count() == 0

    def test_exercise_relationship(self, exercise_created, workout_created):
        plan_data = {
            "name": "Test Exercise Plan",
            "exercise": exercise_created,
            "workout": workout_created,
        }
        plan = ExercisePlan.objects.create(**plan_data)

        assert exercise_created.exercise_plans.count() == 1
        assert exercise_created.exercise_plans.first() == plan

    def test_workout_delete_cascade(self, exercise_created, workout_created):
        plan_data = {
            "name": "Test Exercise Plan",
            "exercise": exercise_created,
            "workout": workout_created,
        }
        ExercisePlan.objects.create(**plan_data)

        assert ExercisePlan.objects.count() == 1
        exercise_created.delete()

        assert ExercisePlan.objects.count() == 0

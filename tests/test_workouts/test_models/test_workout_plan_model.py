import pytest
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError

from apps.workouts.models import WorkoutPlan

pytestmark = [pytest.mark.unit, pytest.mark.django_db]


class TestWorkoutPlanModel:
    def test_create_workout_plan(self, user_created):
        data = {
            "name": "Test Workout Plan",
            "status": "active",
            "is_completed": True,
            "user": user_created,
        }
        workout_plan = WorkoutPlan.objects.create(**data)

        assert workout_plan.id is not None
        assert workout_plan.name == data["name"]
        assert workout_plan.status == data["status"]
        assert workout_plan.is_completed == data["is_completed"]

    def test_default_values(self, user_created):
        data = {
            "name": "Test Workout Plan",
            "user": user_created,
        }
        workout_plan = WorkoutPlan.objects.create(**data)

        assert workout_plan.description == ""
        assert workout_plan.status == "pending"
        assert workout_plan.is_completed == False
        assert workout_plan.started_at is None
        assert workout_plan.finished_at is None

    @pytest.mark.parametrize(
        "field, blank_value",
        [
            ("name", ""),
            ("status", ""),
            ("is_completed", None),
            ("user", None),
        ],
    )
    def test_required_field_cannot_be_empty(self, field, blank_value):
        data = {
            "name": "Test name",
            field: blank_value,
        }

        with pytest.raises(ValidationError):
            workout_plan = WorkoutPlan(**data)
            workout_plan.full_clean()

    @pytest.mark.parametrize(
        "field, invalid_value",
        [
            ("name", "a" * 151),
            ("status", "invalid" * 3),
            ("is_completed", "Invalid completed"),
            ("started_at", "Invalid datetime"),
            ("finished_at", "Invalid datetime"),
        ],
    )
    def test_invalid_field_value(self, field, invalid_value):
        data = {
            "name": "Test Workout Plan",
            field: invalid_value,
        }

        with pytest.raises(ValidationError):
            workout = WorkoutPlan(**data)
            workout.full_clean()

    def test_invalid_user_value(self):
        data = {
            "name": "Test Workout Plan",
            "user": "Invalid user",
        }

        with pytest.raises(ValueError):
            workout = WorkoutPlan(**data)
            workout.full_clean()

    @pytest.mark.parametrize(
        "field, blank_value, default_value",
        [
            ("description", "", ""),
            ("started_at", None, None),
            ("finished_at", None, None),
        ],
    )
    def test_optional_field_can_be_blank(
        self, field, blank_value, default_value, user_created
    ):
        data = {
            "name": "Test Workout Plan",
            "user": user_created,
            field: blank_value,
        }
        workout_plan = WorkoutPlan(**data)
        workout_plan.full_clean()

        assert getattr(workout_plan, field) == default_value

    @pytest.mark.parametrize(
        "field, value",
        [
            ("description", "Test description"),
            ("started_at", timezone.now()),
            ("finished_at", timezone.now()),
        ],
    )
    def test_create_workout_plan_with_optional_fields(self, field, value, user_created):
        data = {
            "name": "Test Workout Plan",
            "user": user_created,
            field: value,
        }
        workout_plan = WorkoutPlan.objects.create(**data)

        assert workout_plan is not None
        assert getattr(workout_plan, field) == value

    def test_str_representation(self, user_created):
        workout_plan = WorkoutPlan(name="Test name", user=user_created)
        assert str(workout_plan) == workout_plan.name

    def test_user_cascade_delete(self, user_created):
        data = {
            "name": "Test Workout Plan",
            "user": user_created,
        }
        workout_plan = WorkoutPlan.objects.create(**data)
        assert workout_plan in WorkoutPlan.objects.all()

        user_created.delete()
        assert workout_plan not in WorkoutPlan.objects.all()

    def test_user_related_name_workout_plans(self, user_created):
        data = {
            "name": "Test Workout Plan",
            "user": user_created,
        }
        workout_plan = WorkoutPlan.objects.create(**data)

        assert user_created.workout_plans.count() == 1
        assert workout_plan in user_created.workout_plans.all()

    def test_set_status_to_active_updates_the_started_at_only_the_first_time(
        self, mocker, user_created
    ):
        current_datetime = timezone.now()
        mocker.patch("apps.workouts.models.timezone.now", return_value=current_datetime)

        # creating the workout plan for the first time with the status "active"
        data = {
            "name": "Test Workout Plan",
            "user": user_created,
            "status": "active",
        }
        workout_plan = WorkoutPlan(**data)
        workout_plan.save()
        static_started_at = workout_plan.started_at

        assert workout_plan.status == "active"
        assert workout_plan.started_at == current_datetime

        # update the workout plan status to something other than "active"
        workout_plan.status = "pending"
        workout_plan.save()

        assert workout_plan.status == "pending"
        assert workout_plan.started_at == static_started_at

        # update the plan status to "active" again
        workout_plan.status = "active"
        workout_plan.save()

        assert workout_plan.status == "active"
        assert workout_plan.started_at == static_started_at

    def test_changing_status_to_finished_updates_the_finished_at_to_the_current_date(
        self, mocker, user_created
    ):
        first_current_datetime = timezone.now()
        second_current_datetime = timezone.now() + timedelta(hours=2)
        mock_timezone = mocker.patch("apps.workouts.models.timezone")
        mock_timezone.now.side_effect = [
            first_current_datetime,
            second_current_datetime,
        ]

        # creating the workout plan for the first time with the status "finished"
        # it should update the finished_at
        data = {
            "name": "Test Workout Plan",
            "user": user_created,
            "status": "finished",
        }
        workout_plan = WorkoutPlan(**data)
        workout_plan.save()

        assert workout_plan.status == "finished"
        assert workout_plan.finished_at == first_current_datetime

        # update the workout plan status to something other than "finished"
        # it should not update finished_at
        workout_plan.status = "pending"
        workout_plan.save()

        assert workout_plan.status == "pending"
        assert workout_plan.finished_at == first_current_datetime

        # update the plan status to "finished" again
        # it should update finished_at
        workout_plan.status = "finished"
        workout_plan.save()

        assert workout_plan.status == "finished"
        assert workout_plan.finished_at == second_current_datetime

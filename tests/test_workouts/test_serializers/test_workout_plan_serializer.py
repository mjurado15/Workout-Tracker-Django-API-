import pytest
from django_mock_queries.query import MockModel

from django.utils import timezone

from apps.workouts.serializers import WorkoutPlanSerializer, WorkoutPlanStatusSerializer


pytestmark = [pytest.mark.unit]


class TestWorkoutPlanSerializer:
    def test_serialize_model(self):
        workout_plan_data = {
            "id": 1,
            "name": "Test Workout Plan",
            "description": "Test description",
            "status": "pending",
            "is_completed": False,
            "created_at": timezone.now(),
        }
        workout_plan = MockModel(**workout_plan_data)

        serializer = WorkoutPlanSerializer(workout_plan)

        expected_data = {
            **workout_plan_data,
            "started_at": None,
            "finished_at": None,
            "created_at": workout_plan_data["created_at"].isoformat()[:-6] + "Z",
        }

        assert serializer.data == expected_data

    def test_valid_data(self):
        data = {
            "name": "Test Workout Plan",
            "description": "Test Description",
        }
        serializer = WorkoutPlanSerializer(data=data)

        assert serializer.is_valid()
        assert set(serializer.validated_data) == {"name", "description"}

    def test_invalid_data(self):
        data = {}
        serializer = WorkoutPlanSerializer(data=data)

        assert not serializer.is_valid()
        assert set(serializer.errors) == {"name"}

    def test_ignore_extra_fields(self):
        data = {
            "name": "Test Workout Plan",
            "description": "Test Description",
            "extra_field": "Extra value",
        }
        serializer = WorkoutPlanSerializer(data=data)

        assert serializer.is_valid()
        assert "extra_field" not in serializer.validated_data

    def test_create_method_adds_the_user_to_the_creation_data(self, mocker):
        workout_plan_data = {
            "name": "Test Workout Plan",
            "description": "Test Description",
        }

        mock_user = mocker.MagicMock(id=1, email="test@test.com")
        mock_request = mocker.MagicMock(user=mock_user)
        mock_create = mocker.patch(
            "apps.workouts.serializers.serializers.ModelSerializer.create",
            return_value=MockModel(id=1, user=mock_user, **workout_plan_data),
        )

        serializer = WorkoutPlanSerializer(
            data=workout_plan_data, context={"request": mock_request}
        )
        serializer.is_valid()
        instance = serializer.create(serializer.validated_data)

        mock_create.assert_called_once_with({**workout_plan_data, "user": mock_user})
        assert instance.id == 1
        assert instance.name == workout_plan_data["name"]
        assert instance.description == workout_plan_data["description"]
        assert instance.user == mock_user


class TestWorkoutPlanStatusSerializer:
    def test_serialize_model(self):
        workout_plan_data = {
            "id": 1,
            "status": "finished",
            "started_at": timezone.now(),
            "finished_at": timezone.now(),
        }
        mock_workout_plan = MockModel(**workout_plan_data)

        serializer = WorkoutPlanStatusSerializer(mock_workout_plan)
        expected_data = {
            **workout_plan_data,
            "started_at": workout_plan_data["started_at"].isoformat()[:-6] + "Z",
            "finished_at": workout_plan_data["finished_at"].isoformat()[:-6] + "Z",
        }

        assert serializer.data == expected_data

    def test_valid_data__status_is_required(self):
        new_data = {}
        serializer = WorkoutPlanStatusSerializer(data=new_data)

        assert not serializer.is_valid()
        assert "status" in serializer.errors

    def test_valid_data_in_update__cannot_set_status_to_finished_if_status_is_pending(
        self,
    ):
        mock_workout_plan = MockModel(id=1, name="Test Workout Plan", status="pending")

        new_data = {"status": "finished"}
        serializer = WorkoutPlanStatusSerializer(mock_workout_plan, data=new_data)

        assert not serializer.is_valid()
        assert (
            str(serializer.errors["status"][0])
            == "The status cannot change directly from pending to finished"
        )

    def test_valid_data_in_update__cannot_set_status_to_pending_if_status_is_finished(
        self,
    ):
        mock_workout_plan = MockModel(id=1, name="Test Workout Plan", status="finished")

        new_data = {"status": "pending"}
        serializer = WorkoutPlanStatusSerializer(mock_workout_plan, data=new_data)

        assert not serializer.is_valid()
        assert (
            str(serializer.errors["status"][0])
            == "The status cannot change from finished to pending"
        )

    @pytest.mark.parametrize("prev_status", ["pending", "finished"])
    def test_valid_data_in_update__status_can_change_to_active_from_any_status(
        self, prev_status
    ):
        mock_workout_plan = MockModel(
            id=1, name="Test Workout Plan", status=prev_status
        )

        new_data = {"status": "active"}
        serializer = WorkoutPlanStatusSerializer(mock_workout_plan, data=new_data)

        assert serializer.is_valid()
        assert set(serializer.validated_data.keys()) == {"status"}

    def test_valid_data_ignores_started_at_and_finished_at_fields(self):
        new_data = {
            "status": "active",
            "started_at": "started_at value",
            "finished_at": "finished_at value",
        }

        serializer = WorkoutPlanStatusSerializer(data=new_data)

        assert serializer.is_valid()
        assert set(serializer.validated_data.keys()) == {"status"}

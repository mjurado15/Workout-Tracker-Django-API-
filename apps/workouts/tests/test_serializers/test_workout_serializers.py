import uuid
from datetime import timedelta
from django.utils import timezone

import pytest
from django_mock_queries.query import MockModel, MockSet

from workouts.serializers import WorkoutSerializer
from workouts.tests.utils import serialize_datetime


pytestmark = [pytest.mark.unit]


class TestWorkoutSerializer:
    @pytest.fixture
    def mock_user(self):
        user_data = {
            "id": uuid.uuid4(),
            "email": "test@test.com",
        }
        return MockModel(**user_data, pk=str(user_data["id"]))

    @pytest.fixture
    def workout_data(self, mock_user):
        return {
            "id": uuid.uuid4(),
            "name": "Test exercise plan",
            "description": "Description",
            "user": mock_user,
            "created_at": timezone.now(),
            "updated_at": timezone.now(),
            "type": None,
        }

    def test_serialize_model(self, workout_data):
        mock_workout = MockModel(**workout_data)
        mock_workout.serializable_value = lambda field_name: getattr(
            mock_workout, field_name
        )

        serializer = WorkoutSerializer(mock_workout)

        expected_data = {
            **workout_data,
            "id": str(workout_data["id"]),
            "created_at": serialize_datetime(workout_data["created_at"]),
            "updated_at": serialize_datetime(workout_data["updated_at"]),
            "user": str(workout_data["user"].id),
            "status": "Pending",
        }
        assert serializer.data == expected_data

    def test_serialize_status__active_scheduled_workout(self, workout_data):
        current_datetime = timezone.now()
        mock_scheduled_dates = MockSet(
            MockModel(datetime=current_datetime - timedelta(hours=2)),
            MockModel(datetime=current_datetime + timedelta(minutes=2)),
        )

        workout_data = {
            **workout_data,
            "type": "S",
            "scheduled_dates": mock_scheduled_dates,
        }
        mock_workout = MockModel(**workout_data)
        mock_workout.serializable_value = lambda field_name: getattr(
            mock_workout, field_name
        )

        serializer = WorkoutSerializer(mock_workout)

        assert serializer.data["type"] == "S"
        assert serializer.data["status"] == "Active"

    def test_serialize_status__completed_scheduled_workout(self, workout_data):
        current_datetime = timezone.now()
        mock_scheduled_dates = MockSet(
            MockModel(datetime=current_datetime - timedelta(hours=2)),
            MockModel(datetime=current_datetime - timedelta(minutes=1)),
        )

        workout_data = {
            **workout_data,
            "type": "S",
            "scheduled_dates": mock_scheduled_dates,
        }
        mock_workout = MockModel(**workout_data)
        mock_workout.serializable_value = lambda field_name: getattr(
            mock_workout, field_name
        )

        serializer = WorkoutSerializer(mock_workout)

        assert serializer.data["type"] == "S"
        assert serializer.data["status"] == "Completed"

    def test_serialize_status__active_recurrent_workout(self, workout_data):
        workout_data = {
            **workout_data,
            "type": "R",
        }
        mock_workout = MockModel(**workout_data)
        mock_workout.serializable_value = lambda field_name: getattr(
            mock_workout, field_name
        )

        serializer = WorkoutSerializer(mock_workout)

        assert serializer.data["type"] == "R"
        assert serializer.data["status"] == "Active"

    def test_valid_data(self):
        workout_data = {
            "name": "Test workout",
            "description": "Description",
        }
        serializer = WorkoutSerializer(data=workout_data)

        assert serializer.is_valid()
        assert set(serializer.validated_data.keys()) == set(workout_data.keys())

    def test_invalid_data(self):
        workout_data = {}
        serializer = WorkoutSerializer(data=workout_data)

        assert not serializer.is_valid()
        assert serializer.errors != {}

    def test_ignore_extra_fields(self):
        workout_data = {
            "name": "Test workout",
            "description": "Description",
            "extra_field": "extra_value",
        }
        serializer = WorkoutSerializer(data=workout_data)

        assert serializer.is_valid()
        assert "extra_field" not in serializer.validated_data

    def test_create_method_adds_the_user(self, mocker):
        mock_user = MockModel(id=uuid.uuid4(), email="test@test.com")
        mock_request = mocker.MagicMock(user=mock_user)

        workout_data = {
            "name": "Test workout",
            "description": "Description",
        }

        mock_model_create = mocker.patch(
            "workouts.serializers.serializers.ModelSerializer.create",
            return_value=MockModel(id=uuid.uuid4(), **workout_data, user=mock_user),
        )

        serializer = WorkoutSerializer(
            data=workout_data, context={"request": mock_request}
        )
        serializer.is_valid()
        serializer.create(serializer.validated_data)

        mock_model_create.assert_called_once_with(
            {**serializer.validated_data, "user": mock_user}
        )

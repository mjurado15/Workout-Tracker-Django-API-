import uuid
from django.utils import timezone

import pytest
from django_mock_queries.query import MockModel

from workouts.serializers import ScheduledDateSerializer
from workouts.tests.utils import serialize_datetime


pytestmark = [pytest.mark.unit]


class TestScheduledDateSerializer:
    def test_serialize_model(self):
        workout_data = {"id": uuid.uuid4()}
        mock_workout = MockModel(**workout_data, pk=str(workout_data["id"]))

        scheduled_data = {
            "datetime": timezone.now(),
            "workout": mock_workout,
        }
        mock_scheduled_date = MockModel(**scheduled_data)
        mock_scheduled_date.serializable_value = lambda field_name: getattr(
            mock_scheduled_date, field_name
        )

        serializer = ScheduledDateSerializer(mock_scheduled_date)

        expected_data = {
            "datetime": serialize_datetime(scheduled_data["datetime"]),
            "workout": str(scheduled_data["workout"].id),
        }
        assert serializer.data == expected_data

    def test_valid_data(self):
        scheduled_data = {
            "datetime": "2024-03-12 19:30:00",
        }
        serializer = ScheduledDateSerializer(data=scheduled_data)

        assert serializer.is_valid()
        assert set(serializer.validated_data.keys()) == set(scheduled_data.keys())

    def test_invalid_data(self):
        scheduled_data = {}
        serializer = ScheduledDateSerializer(data=scheduled_data)

        assert not serializer.is_valid()
        assert serializer.errors != {}

    def test_create_method_adds_the_workout(self, mocker):
        mock_workout = MockModel(id=uuid.uuid4())

        scheduled_data = {
            "datetime": "2024-03-12 19:30:00",
        }
        mock_modelserializer_create = mocker.patch(
            "workouts.serializers.serializers.ModelSerializer.create",
            return_value=MockModel(
                id=uuid.uuid4(), **scheduled_data, workout=mock_workout
            ),
        )

        serializer = ScheduledDateSerializer(
            data=scheduled_data, context={"workout": mock_workout}
        )
        assert serializer.is_valid()
        serializer.create(serializer.validated_data)

        mock_modelserializer_create.assert_called_once_with(
            {**serializer.validated_data, "workout": mock_workout}
        )

import uuid
from django.utils import timezone

import pytest
from django_mock_queries.query import MockModel

from workouts.serializers import RecurringAlertSerializer


pytestmark = [pytest.mark.unit]


class TestRecurringAlertSerializer:
    def test_serialize_model(self):
        workout_data = {"id": uuid.uuid4()}
        mock_workout = MockModel(**workout_data, pk=str(workout_data["id"]))

        alert_data = {
            "time": timezone.now().time(),
            "week_days": [0, 1],
            "workout": mock_workout,
        }
        mock_recurring_alert = MockModel(**alert_data)
        mock_recurring_alert.serializable_value = lambda field_name: getattr(
            mock_recurring_alert, field_name
        )

        serializer = RecurringAlertSerializer(mock_recurring_alert)

        expected_data = {
            "time": str(alert_data["time"]),
            "week_days": alert_data["week_days"],
            "workout": str(workout_data["id"]),
        }
        assert serializer.data == expected_data

    def test_valid_data(self):
        alert_data = {
            "time": "19:30:00",
            "week_days": [0, 1, 2],
        }
        serializer = RecurringAlertSerializer(data=alert_data)

        assert serializer.is_valid()
        assert set(serializer.validated_data.keys()) == set(alert_data.keys())

    def test_invalid_data(self):
        alert_data = {}
        serializer = RecurringAlertSerializer(data=alert_data)

        assert not serializer.is_valid()
        assert serializer.errors != {}

    def test_validate_week_days__duplicate_values_are_not_allowed(self):
        alert_data = {
            "time": "19:30:00",
            "week_days": [0, 1, 2, 2],
        }
        serializer = RecurringAlertSerializer(data=alert_data)

        assert not serializer.is_valid()
        assert (
            str(serializer.errors["week_days"][0]) == "Duplicate values are not allowed"
        )

    def test_create_method_adds_the_workout(self, mocker):
        mock_workout = MockModel(id=uuid.uuid4())

        alert_data = {
            "time": "19:30:00",
            "week_days": [0, 1, 2],
        }
        mock_modelserializer_create = mocker.patch(
            "workouts.serializers.serializers.ModelSerializer.create",
            return_value=MockModel(id=uuid.uuid4(), **alert_data, workout=mock_workout),
        )

        serializer = RecurringAlertSerializer(
            data=alert_data, context={"workout": mock_workout}
        )
        assert serializer.is_valid()
        serializer.create(serializer.validated_data)

        mock_modelserializer_create.assert_called_once_with(
            {**serializer.validated_data, "workout": mock_workout}
        )

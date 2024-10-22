import uuid
from django.utils import timezone

import pytest
from django_mock_queries.query import MockModel

from workouts.serializers import CommentSerializer
from workouts.tests.utils import serialize_datetime


pytestmark = [pytest.mark.unit]


class TestCommentSerializer:
    def test_serialize_model(self):
        workout_data = {"id": uuid.uuid4(), "name": "Test Workout"}
        mock_workout = MockModel(**workout_data, pk=str(workout_data["id"]))

        comment_data = {
            "id": uuid.uuid4(),
            "comment": "This is a comment",
            "workout": mock_workout,
            "created_at": timezone.now(),
            "updated_at": timezone.now(),
        }
        mock_comment = MockModel(**comment_data)
        mock_comment.serializable_value = lambda field_name: getattr(
            mock_comment, field_name
        )

        serializer = CommentSerializer(mock_comment)
        expected_data = {
            **comment_data,
            "id": str(comment_data["id"]),
            "workout": str(comment_data["workout"].id),
            "created_at": serialize_datetime(comment_data["created_at"]),
            "updated_at": serialize_datetime(comment_data["updated_at"]),
        }

        assert serializer.data == expected_data

    def test_valid_data(self):
        comment_data = {"comment": "This is a comment"}
        serializer = CommentSerializer(data=comment_data)

        assert serializer.is_valid()
        assert set(serializer.validated_data.keys()) == set(comment_data.keys())

    def test_invalid_data(self):
        comment_data = {}
        serializer = CommentSerializer(data=comment_data)

        assert not serializer.is_valid()
        assert serializer.errors != {}

    def test_create_method_add_the_workout(self, mocker):
        comment_data = {"comment": "This is a comment"}

        workout_data = {"id": uuid.uuid4()}
        mock_workout = MockModel(**workout_data)

        mock_modelserializer_create = mocker.patch(
            "workouts.serializers.serializers.ModelSerializer.create",
            return_value=MockModel(
                id=uuid.uuid4(), **comment_data, workout=mock_workout
            ),
        )

        serializer = CommentSerializer(
            data=comment_data, context={"workout": mock_workout}
        )
        serializer.is_valid()
        instance = serializer.create(serializer.validated_data)

        mock_modelserializer_create.assert_called_once_with(
            {**comment_data, "workout": mock_workout}
        )
        assert instance.id is not None
        assert instance.comment == comment_data["comment"]

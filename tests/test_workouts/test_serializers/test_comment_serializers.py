import pytest
from django_mock_queries.query import MockModel

from apps.workouts.serializers import WorkoutCommentSerializer


pytestmark = [pytest.mark.unit]


class TestWorkoutCommentSerializer:
    def test_serialize_model(self):
        mock_workout_plan = MockModel(pk=1, id=1, name="Test Workout Plan")
        comment_data = {
            "id": 2,
            "comment": "This is a comment",
            "workout_plan": mock_workout_plan,
        }

        mock_comment = MockModel(**comment_data)
        mock_comment.serializable_value = lambda field_name: getattr(
            mock_comment, field_name
        )

        serializer = WorkoutCommentSerializer(mock_comment)
        expected_data = {**comment_data, "workout_plan": 1}

        assert serializer.data == expected_data

    def test_valid_data(self):
        comment_data = {
            "comment": "This is a comment",
        }
        serializer = WorkoutCommentSerializer(data=comment_data)

        assert serializer.is_valid()
        assert set(serializer.validated_data) == {"comment"}

    def test_invalid_data(self):
        comment_data = {}
        serializer = WorkoutCommentSerializer(data=comment_data)

        assert not serializer.is_valid()
        assert serializer.errors != {}

    @pytest.mark.parametrize(
        "field, value",
        [
            ("workout_plan", 23),
            ("created_at", "2024-03-23"),
            ("updated_at", "2024-04-23"),
        ],
    )
    def test_ignore_read_only_fields(self, field, value):
        comment_data = {
            "comment": "This is a comment",
            field: value,
        }
        serializer = WorkoutCommentSerializer(data=comment_data)

        assert serializer.is_valid()
        assert field not in serializer.validated_data

    def test_ignore_extra_fields(self):
        comment_data = {
            "comment": "This is a comment",
            "extra_field": "Extra field",
        }
        serializer = WorkoutCommentSerializer(data=comment_data)

        assert serializer.is_valid()
        assert "extra_field" not in serializer.validated_data

    def test_create_method_adds_the_workout_plan(self, mocker):
        comment_data = {
            "comment": "This is a comment",
        }

        mock_workout_plan = MockModel(id=1, name="Test Workout Plan")
        mock_super_create = mocker.patch(
            "apps.workouts.serializers.serializers.ModelSerializer.create",
            return_value=MockModel(
                id=1, **comment_data, workout_plan=mock_workout_plan
            ),
        )

        serializer = WorkoutCommentSerializer(
            data=comment_data, context={"workout_plan": mock_workout_plan}
        )

        serializer.is_valid()
        instance = serializer.create(serializer.validated_data)

        mock_super_create.assert_called_once_with(
            {**comment_data, "workout_plan": mock_workout_plan}
        )
        assert instance.id == 1
        assert instance.comment == comment_data["comment"]
        assert instance.workout_plan == mock_workout_plan

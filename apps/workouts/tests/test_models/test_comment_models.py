import pytest

from workouts.models import WorkoutComment


pytestmark = [pytest.mark.unit, pytest.mark.django_db]


class TestWorkoutCommentModel:
    def test_create_comment(self, workout_created):
        comment_data = {
            "comment": "This is a comment",
            "workout": workout_created,
        }

        comment = WorkoutComment.objects.create(**comment_data)

        assert comment.id is not None
        assert all(getattr(comment, field) for field in comment_data)

    def test_comment_str(self, workout_created):
        comment_data = {
            "comment": "This is a comment",
            "workout": workout_created,
        }
        comment = WorkoutComment(**comment_data)

        assert str(comment) == f"{comment.id} ({workout_created.name})"

    def test_workout_comments_relationship(self, workout_created):
        comment_data = {
            "comment": "This is a comment",
            "workout": workout_created,
        }
        comment = WorkoutComment.objects.create(**comment_data)

        assert workout_created.comments.count() == 1
        assert workout_created.comments.first() == comment

    def test_workout_cascade_delete(self, workout_created):
        comment_data = {
            "comment": "This is a comment",
            "workout": workout_created,
        }
        WorkoutComment.objects.create(**comment_data)

        assert WorkoutComment.objects.count() == 1
        workout_created.delete()

        assert WorkoutComment.objects.count() == 0

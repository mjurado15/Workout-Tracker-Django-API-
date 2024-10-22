import uuid

import pytest
from django.urls import reverse

from workouts.models import WorkoutComment
from workouts.tests.utils import serialize_datetime


pytestmark = [pytest.mark.integration, pytest.mark.django_db]


class ParentWorkoutCommentView:
    url = reverse("workouts-list")
    comments_url = "comments/"

    def create_expected_comment(self, comment):
        comment_dict = {**comment.__dict__}
        comment_dict.pop("_state")
        comment_dict.pop("workout_id")

        comment_dict["id"] = str(comment_dict["id"])
        comment_dict["created_at"] = serialize_datetime(comment_dict["created_at"])
        comment_dict["updated_at"] = serialize_datetime(comment_dict["updated_at"])

        comment_dict["workout"] = str(comment.workout.id)

        return comment_dict


class TestListCommentsView(ParentWorkoutCommentView):
    def test_user_can_only_access_comments_of_their_workout(
        self,
        api_client,
        create_batch_workouts_with,
        create_batch_comments_with,
        create_comment_with,
        list_response_keys,
    ):
        [target_workout, other_workout] = create_batch_workouts_with(size=2)
        create_batch_comments_with(size=2, workout=other_workout)
        comment_1 = create_comment_with(workout=target_workout)
        comment_2 = create_comment_with(workout=target_workout)
        comment_3 = create_comment_with(workout=target_workout)

        authenticated_user = target_workout.user
        workout_id = str(target_workout.id)

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.get(
            f"{self.url}{workout_id}/{self.comments_url}", format="json"
        )

        assert response.status_code == 200
        assert set(response.data.keys()) == list_response_keys

        sorted_comments = [comment_3, comment_2, comment_1]
        expected_comments = [
            self.create_expected_comment(item) for item in sorted_comments
        ]

        assert response.json()["results"] == expected_comments

    def test_user_cannnot_access_comments_of_another_user_s_workout(
        self,
        api_client,
        workout_created,
        create_batch_comments_with,
        user_created,
    ):
        target_workout = workout_created
        workout_id = str(target_workout.id)
        create_batch_comments_with(size=3, workout=target_workout)

        authenticated_user = user_created

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.get(
            f"{self.url}{workout_id}/{self.comments_url}", format="json"
        )

        assert authenticated_user.id != target_workout.user.id
        assert response.status_code == 404
        assert response.json()["detail"] == "No Workout matches the given query."

    def test_user_cannnot_access_comments_of_workout_that_not_exist(
        self, api_client, user_created
    ):
        workout_id = uuid.uuid4()
        authenticated_user = user_created

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.get(
            f"{self.url}{workout_id}/{self.comments_url}", format="json"
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "No Workout matches the given query."

    def test_unauthenticated_user_cannot_access_comments(
        self, api_client, workout_created
    ):
        workout_id = str(workout_created.id)

        response = response = api_client.get(
            f"{self.url}{workout_id}/{self.comments_url}", format="json"
        )

        assert response.status_code == 401


class TestRetrieveCommentView(ParentWorkoutCommentView):
    def test_user_can_access_comment_of_his_workout(self, api_client, comment_created):
        workout = comment_created.workout
        workout_id = str(workout.id)
        comment_id = str(comment_created.id)

        authenticated_user = workout.user

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.get(
            f"{self.url}{workout_id}/{self.comments_url}{comment_id}/",
            format="json",
        )

        assert response.status_code == 200
        expected_data = self.create_expected_comment(comment_created)

        assert response.json() == expected_data

    def test_user_cannot_access_comment_that_not_exist(
        self, api_client, workout_created
    ):
        authenticated_user = workout_created.user

        workout_id = str(workout_created.id)
        comment_id = str(uuid.uuid4())

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.get(
            f"{self.url}{workout_id}/{self.comments_url}{comment_id}/",
            format="json",
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "No WorkoutComment matches the given query."

    def test_user_cannot_access_comment_of_another_user_s_workout(
        self, api_client, user_created, comment_created
    ):
        authenticated_user = user_created

        workout = comment_created.workout
        workout_id = str(workout.id)
        comment_id = str(comment_created.id)

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.get(
            f"{self.url}{workout_id}/{self.comments_url}{comment_id}/",
            format="json",
        )

        assert authenticated_user.id != workout.user.id
        assert response.status_code == 404
        assert response.json()["detail"] == "No Workout matches the given query."

    def test_user_cannot_access_comments_of_workout_that_not_exist(
        self, api_client, user_created
    ):
        authenticated_user = user_created

        workout_id = str(uuid.uuid4())
        comment_id = str(uuid.uuid4())

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.get(
            f"{self.url}{workout_id}/{self.comments_url}{comment_id}/",
            format="json",
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "No Workout matches the given query."

    def test_unauthenticated_user_cannot_access_comment(
        self, api_client, comment_created
    ):
        workout_id = str(comment_created.workout.id)
        exercise_plan_id = str(comment_created.id)

        response = api_client.get(
            f"{self.url}{workout_id}/{self.comments_url}{exercise_plan_id}/",
            format="json",
        )

        assert response.status_code == 401


class TestCreateCommentView(ParentWorkoutCommentView):
    def test_create_comment(self, api_client, workout_created):
        authenticated_user = workout_created.user
        workout_id = str(workout_created.id)

        comment_data = {
            "comment": "Test workout comment",
        }

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.post(
            f"{self.url}{workout_id}/{self.comments_url}",
            comment_data,
            format="json",
        )

        assert response.status_code == 201
        assert WorkoutComment.objects.count() == 1
        comment_created = WorkoutComment.objects.first()

        assert all(
            getattr(comment_created, field) == comment_data[field]
            for field in comment_data
        )

        expected_data = self.create_expected_comment(comment_created)
        assert response.json() == expected_data

    def test_create_fails_with_incorrect_data(self, api_client, workout_created):
        workout_id = str(workout_created.id)
        authenticated_user = workout_created.user

        comment_data = {}

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.post(
            f"{self.url}{workout_id}/{self.comments_url}",
            comment_data,
            format="json",
        )

        assert response.status_code == 400
        assert WorkoutComment.objects.count() == 0
        assert response.json() != {}

    def test_create_fails_if_workout_not_exist(self, api_client, user_created):
        workout_id = str(uuid.uuid4())
        comment_data = {
            "comment": "Test workout comment",
        }

        api_client.force_authenticate(user=user_created)
        response = api_client.post(
            f"{self.url}{workout_id}/{self.comments_url}",
            comment_data,
            format="json",
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "No Workout matches the given query."

    def test_unauthenticate_user_cannot_create_comment(
        self, api_client, workout_created
    ):
        workout_id = str(workout_created.id)
        comment_data = {
            "comment": "Test workout comment",
        }

        response = api_client.post(
            f"{self.url}{workout_id}/{self.comments_url}",
            comment_data,
            format="json",
        )
        assert response.status_code == 401


class TestPartialUpdateCommentView(ParentWorkoutCommentView):
    def test_user_can_partial_update_comment_of_his_workout(
        self, api_client, comment_created
    ):
        workout = comment_created.workout
        workout_id = str(workout.id)
        authenticated_user = workout.user

        old_comment = comment_created
        comment_id = str(old_comment.id)

        new_data = {
            "comment": "This is a new comment",
        }

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.patch(
            f"{self.url}{workout_id}/{self.comments_url}{comment_id}/",
            new_data,
            format="json",
        )

        assert response.status_code == 200
        updated_comment = WorkoutComment.objects.get(id=old_comment.id)

        assert all(
            getattr(updated_comment, field) == new_data[field] for field in new_data
        )
        expected_data = self.create_expected_comment(updated_comment)

        assert response.json() == expected_data

    def test_user_cannot_partial_update_comment_that_not_exist(
        self, api_client, workout_created
    ):
        workout_id = str(workout_created.id)
        authenticated_user = workout_created.user

        comment_id = str(uuid.uuid4())

        new_data = {"comment": "This is a new comment"}

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.patch(
            f"{self.url}{workout_id}/{self.comments_url}{comment_id}/",
            new_data,
            format="json",
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "No WorkoutComment matches the given query."

    def test_user_cannot_partial_update_comment_of_another_user_s_workout(
        self, api_client, user_created, exercise_plan_created
    ):
        authenticated_user = user_created

        workout = exercise_plan_created.workout
        workout_id = str(workout.id)

        old_comment = exercise_plan_created
        comment_id = str(old_comment.id)

        new_data = {"comment": "This is a new comment"}

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.patch(
            f"{self.url}{workout_id}/{self.comments_url}{comment_id}/",
            new_data,
            format="json",
        )

        assert authenticated_user.id != workout.user.id
        assert response.status_code == 404
        assert response.json()["detail"] == "No Workout matches the given query."

    def test_user_cannot_partial_update_comment_of_workout_that_not_exist(
        self, api_client, user_created
    ):
        authenticated_user = user_created
        workout_id = str(uuid.uuid4())
        comment_id = str(uuid.uuid4())

        new_data = {"comment": "This is a new comment"}

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.patch(
            f"{self.url}{workout_id}/{self.comments_url}{comment_id}/",
            new_data,
            format="json",
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "No Workout matches the given query."

    def test_partial_update_comment_not_fail_with_incomplete_data(
        self, api_client, comment_created
    ):
        workout = comment_created.workout
        workout_id = str(workout.id)
        authenticated_user = workout.user

        old_comment = comment_created
        comment_id = str(old_comment.id)

        new_data = {}

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.patch(
            f"{self.url}{workout_id}/{self.comments_url}{comment_id}/",
            new_data,
            format="json",
        )

        assert response.status_code == 200
        updated_comment = WorkoutComment.objects.get(id=old_comment.id)
        expected_data = self.create_expected_comment(updated_comment)

        assert response.json() == expected_data

    def test_unauthenticated_user_cannot_partial_update_comment(
        self, api_client, comment_created
    ):
        workout = comment_created.workout
        workout_id = str(workout.id)

        old_comment = comment_created
        comment_id = str(old_comment.id)

        new_data = {"comment": "This is a new comment"}

        response = api_client.patch(
            f"{self.url}{workout_id}/{self.comments_url}{comment_id}/",
            new_data,
            format="json",
        )

        assert response.status_code == 401


class TestDeleteCommentView(ParentWorkoutCommentView):
    def test_user_can_delete_comment_of_his_workout(self, api_client, comment_created):
        workout = comment_created.workout
        workout_id = str(workout.id)

        authenticated_user = workout.user

        comment_id = str(comment_created.id)

        assert WorkoutComment.objects.count() == 1

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.delete(
            f"{self.url}{workout_id}/{self.comments_url}{comment_id}/",
            format="json",
        )

        assert response.status_code == 204
        assert WorkoutComment.objects.count() == 0

    def test_user_cannot_delete_comment_that_not_exist(
        self, api_client, workout_created
    ):
        authenticated_user = workout_created.user

        workout_id = str(workout_created.id)
        comment_id = str(uuid.uuid4())

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.delete(
            f"{self.url}{workout_id}/{self.comments_url}{comment_id}/",
            format="json",
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "No WorkoutComment matches the given query."

    def test_user_cannot_delete_comment_of_another_user_s_workout(
        self, api_client, user_created, comment_created
    ):
        workout = comment_created.workout
        workout_id = str(workout.id)
        comment_id = str(comment_created.id)

        api_client.force_authenticate(user=user_created)
        response = api_client.delete(
            f"{self.url}{workout_id}/{self.comments_url}{comment_id}/",
            format="json",
        )

        assert user_created.id != workout.user.id
        assert response.status_code == 404
        assert response.json()["detail"] == "No Workout matches the given query."

    def test_user_cannot_delete_comment_of_workout_that_not_exist(
        self, api_client, user_created
    ):
        workout_id = str(uuid.uuid4())
        comment_id = str(uuid.uuid4())

        api_client.force_authenticate(user=user_created)
        response = api_client.delete(
            f"{self.url}{workout_id}/{self.comments_url}{comment_id}/",
            format="json",
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "No Workout matches the given query."

    def test_unauthenticated_user_cannot_delete_comments(
        self, api_client, comment_created
    ):
        workout = comment_created.workout
        workout_id = str(workout.id)
        comment_id = str(comment_created.id)

        response = response = api_client.delete(
            f"{self.url}{workout_id}/{self.comments_url}{comment_id}/",
            format="json",
        )

        assert response.status_code == 401

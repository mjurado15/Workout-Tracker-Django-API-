import pytest
from django.urls import reverse

from apps.workouts.models import WorkoutComment


pytestmark = [pytest.mark.integration, pytest.mark.django_db]


global_url = reverse("workout-plans-list")
extra_comments_url = "comments/"


class TestListCommentView:
    def test_user_can_access_comments_of_his_workout_plan(
        self, api_client, create_batch_comments_with, workout_plan_created
    ):
        authenticated_user = workout_plan_created.user
        comments = create_batch_comments_with(size=3, workout_plan=workout_plan_created)

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.get(
            f"{global_url}{workout_plan_created.id}/{extra_comments_url}", format="json"
        )

        assert response.status_code == 200
        assert len(response.data["results"]) == len(comments)

        response_comments = {item["id"] for item in response.data["results"]}
        expected_comments = {item.id for item in comments}

        assert response_comments == expected_comments

    def test_user_cannot_access_comments_of_another_user_s_workout_plan(
        self, api_client, comment_created, user_created
    ):
        workout_plan = comment_created.workout_plan
        another_user = comment_created.workout_plan.user

        api_client.force_authenticate(user=user_created)
        response = api_client.get(
            f"{global_url}{workout_plan.id}/{extra_comments_url}", format="json"
        )

        assert another_user.id != user_created.id
        assert response.status_code == 404
        assert str(response.data["detail"]) == "No WorkoutPlan matches the given query."

    def test_user_cannot_access_comments_for_workout_plan_that_not_exist(
        self, api_client, user_created
    ):
        api_client.force_authenticate(user=user_created)
        response = api_client.get(
            f"{global_url}{12}/{extra_comments_url}", format="json"
        )

        assert response.status_code == 404
        assert str(response.data["detail"]) == "No WorkoutPlan matches the given query."

    def test_unauthenticated_user_cannot_access_comments(
        self, api_client, comment_created
    ):
        workout_plan = comment_created.workout_plan
        response = api_client.get(
            f"{global_url}{workout_plan.id}/{extra_comments_url}", format="json"
        )

        assert response.status_code == 401


class TestCreateCommentView:
    def test_user_can_create_comment_for_his_workout_plan(
        self, api_client, workout_plan_created
    ):
        assert WorkoutComment.objects.count() == 0
        auth_user = workout_plan_created.user
        comment_data = {
            "comment": "This is a comment",
        }

        api_client.force_authenticate(user=auth_user)
        response = api_client.post(
            f"{global_url}{workout_plan_created.id}/{extra_comments_url}",
            comment_data,
            format="json",
        )

        assert WorkoutComment.objects.count() == 1
        comment_created = WorkoutComment.objects.first()
        assert comment_created.comment == comment_data["comment"]

        expected_data = {
            "id": comment_created.id,
            "comment": comment_data["comment"],
            "workout_plan": workout_plan_created.id,
            "created_at": comment_created.created_at.isoformat()[:-6] + "Z",
            "updated_at": comment_created.updated_at.isoformat()[:-6] + "Z",
        }

        assert response.status_code == 201
        assert response.data == expected_data

    def test_user_cannot_create_comment_for_another_user_s_workout_plan(
        self, api_client, workout_plan_created, user_created
    ):
        comment_data = {
            "comment": "This is a comment",
        }

        api_client.force_authenticate(user=user_created)
        response = api_client.post(
            f"{global_url}{workout_plan_created.id}/{extra_comments_url}",
            comment_data,
            format="json",
        )

        assert workout_plan_created.user.id != user_created
        assert response.status_code == 404
        assert str(response.data["detail"]) == "No WorkoutPlan matches the given query."

    def test_user_cannot_create_comment_for_workout_plan_that_not_exist(
        self, api_client, user_created
    ):
        comment_data = {
            "comment": "This is a comment",
        }

        api_client.force_authenticate(user=user_created)
        response = api_client.post(
            f"{global_url}{3}/{extra_comments_url}", comment_data, format="json"
        )

        assert response.status_code == 404
        assert str(response.data["detail"]) == "No WorkoutPlan matches the given query."

    def test_creation_fails_with_incorrect_data(self, api_client, workout_plan_created):
        auth_user = workout_plan_created.user
        comment_data = {}

        api_client.force_authenticate(user=auth_user)
        response = api_client.post(
            f"{global_url}{workout_plan_created.id}/{extra_comments_url}",
            comment_data,
            format="json",
        )

        assert response.status_code == 400
        assert response.data != {}

    def test_unauthenticated_user_cannot_create_comment(
        self, api_client, workout_plan_created
    ):
        comment_data = {
            "comment": "This is a comment",
        }
        response = api_client.post(
            f"{global_url}{workout_plan_created.id}/{extra_comments_url}",
            comment_data,
            format="json",
        )

        assert response.status_code == 401


class TestRetrieveCommentView:
    def test_user_can_retrieve_comment_of_his_workout_plan(
        self, api_client, comment_created
    ):
        workout_plan = comment_created.workout_plan
        auth_user = comment_created.workout_plan.user

        api_client.force_authenticate(user=auth_user)
        response = api_client.get(
            f"{global_url}{workout_plan.id}/{extra_comments_url}{comment_created.id}/",
            format="json",
        )

        expected_data = {
            "id": comment_created.id,
            "comment": comment_created.comment,
            "workout_plan": workout_plan.id,
            "created_at": comment_created.created_at.isoformat()[:-6] + "Z",
            "updated_at": comment_created.updated_at.isoformat()[:-6] + "Z",
        }

        assert response.status_code == 200
        assert response.data == expected_data

    def test_user_cannot_retrieve_comment_of_another_user_s_workout_plan(
        self, api_client, comment_created, user_created
    ):
        workout_plan = comment_created.workout_plan
        another_user = comment_created.workout_plan.user

        api_client.force_authenticate(user=user_created)
        response = api_client.get(
            f"{global_url}{workout_plan.id}/{extra_comments_url}{comment_created.id}/",
            format="json",
        )

        assert another_user.id != user_created
        assert response.status_code == 404
        assert str(response.data["detail"]) == "No WorkoutPlan matches the given query."

    def test_user_cannot_retrieve_comment_of_workout_plan_that_not_exist(
        self, api_client, user_created
    ):
        api_client.force_authenticate(user=user_created)
        response = api_client.get(
            f"{global_url}{10}/{extra_comments_url}{1}/", format="json"
        )

        assert response.status_code == 404
        assert str(response.data["detail"]) == "No WorkoutPlan matches the given query."

    def test_user_cannot_retrieve_comment_that_not_exist(
        self, api_client, workout_plan_created
    ):
        auth_user = workout_plan_created.user

        api_client.force_authenticate(user=auth_user)
        response = api_client.get(
            f"{global_url}{workout_plan_created.id}/{extra_comments_url}{1}/",
            format="json",
        )

        assert response.status_code == 404
        assert (
            str(response.data["detail"]) == "No WorkoutComment matches the given query."
        )

    def test_unauthenticated_user_cannot_retrieve_comment(
        self, api_client, comment_created
    ):
        workout_plan = comment_created.workout_plan

        response = api_client.get(
            f"{global_url}{workout_plan.id}/{extra_comments_url}{comment_created.id}/",
            format="json",
        )

        assert response.status_code == 401


class TestUpdateCommentView:
    def test_can_update_comment_of_his_workout_plan(
        self, api_client, comment_created, comment_built
    ):
        auth_user = comment_created.workout_plan.user

        old_comment = comment_created
        new_comment_data = {
            "comment": comment_built.comment,
        }

        api_client.force_authenticate(user=auth_user)
        response = api_client.put(
            f"{global_url}{old_comment.workout_plan.id}/{extra_comments_url}{old_comment.id}/",
            new_comment_data,
            format="json",
        )

        comment_updated = WorkoutComment.objects.filter(id=comment_created.id).first()
        expected_data = {
            "id": old_comment.id,
            "comment": new_comment_data["comment"],
            "workout_plan": comment_created.workout_plan.id,
            "created_at": comment_created.created_at.isoformat()[:-6] + "Z",
            "updated_at": comment_updated.updated_at.isoformat()[:-6] + "Z",
        }

        assert response.status_code == 200
        assert response.data == expected_data

    def test_cannot_update_comment_with_incorrect_data(
        self, api_client, comment_created
    ):
        auth_user = comment_created.workout_plan.user

        old_comment = comment_created
        new_comment_data = {}

        api_client.force_authenticate(user=auth_user)
        response = api_client.put(
            f"{global_url}{old_comment.workout_plan.id}/{extra_comments_url}{old_comment.id}/",
            new_comment_data,
            format="json",
        )

        assert response.status_code == 400
        assert response.data != {}

    def test_cannot_update_comment_of_another_user_s_workout_plan(
        self, api_client, comment_created, user_created
    ):
        old_comment = comment_created
        new_comment_data = {
            "comment": "Test comment",
        }

        api_client.force_authenticate(user=user_created)
        response = api_client.put(
            f"{global_url}{old_comment.workout_plan.id}/{extra_comments_url}{old_comment.id}/",
            new_comment_data,
            format="json",
        )

        assert old_comment.workout_plan.user.id != user_created.id
        assert response.status_code == 404
        assert response.data["detail"] == "No WorkoutPlan matches the given query."

    def test_cannot_update_comment_of_workout_plan_that_not_exist(
        self, api_client, user_created
    ):
        new_comment_data = {
            "comment": "Test comment",
        }

        api_client.force_authenticate(user=user_created)
        response = api_client.put(
            f"{global_url}{12}/{extra_comments_url}{1}/",
            new_comment_data,
            format="json",
        )

        assert response.status_code == 404
        assert str(response.data["detail"]) == "No WorkoutPlan matches the given query."

    def test_cannot_update_comment_that_not_exist(
        self, api_client, workout_plan_created
    ):
        auth_user = workout_plan_created.user
        new_comment_data = {
            "comment": "Test comment",
        }

        api_client.force_authenticate(user=auth_user)
        response = api_client.put(
            f"{global_url}{workout_plan_created.id}/{extra_comments_url}{1}/",
            new_comment_data,
            format="json",
        )

        assert response.status_code == 404
        assert (
            str(response.data["detail"]) == "No WorkoutComment matches the given query."
        )

    def test_unauthenticated_user_cannot_update_comment(
        self, api_client, comment_created
    ):
        old_comment = comment_created
        new_comment_data = {
            "comment": "Test comment",
        }

        response = api_client.put(
            f"{global_url}{old_comment.workout_plan.id}/{extra_comments_url}{old_comment.id}/",
            new_comment_data,
            format="json",
        )

        assert response.status_code == 401


class TestDeleteCommentView:
    def test_can_delete_comment_of_his_workout_plan(self, api_client, comment_created):
        workout_plan = comment_created.workout_plan
        auth_user = workout_plan.user

        assert WorkoutComment.objects.filter(id=comment_created.id).exists()

        api_client.force_authenticate(user=auth_user)
        response = api_client.delete(
            f"{global_url}{workout_plan.id}/{extra_comments_url}{comment_created.id}/",
            format="json",
        )

        assert response.status_code == 204
        assert not WorkoutComment.objects.filter(id=comment_created.id).exists()

    def test_cannot_delete_comment_of_another_user_s_workout_plan(
        self, api_client, comment_created, user_created
    ):
        workout_plan = comment_created.workout_plan
        another_user = workout_plan.user

        api_client.force_authenticate(user=user_created)
        response = api_client.delete(
            f"{global_url}{workout_plan.id}/{extra_comments_url}{comment_created.id}/",
            format="json",
        )

        assert another_user.id != user_created.id
        assert response.status_code == 404
        assert str(response.data["detail"]) == "No WorkoutPlan matches the given query."

    def test_cannot_delete_comment_of_workout_plan_that_not_exist(
        self, api_client, user_created
    ):
        api_client.force_authenticate(user=user_created)
        response = api_client.delete(
            f"{global_url}{12}/{extra_comments_url}{1}/",
            format="json",
        )

        assert response.status_code == 404
        assert str(response.data["detail"]) == "No WorkoutPlan matches the given query."

    def test_cannot_delete_comment_that_not_exist(
        self, api_client, workout_plan_created
    ):
        auth_user = workout_plan_created.user

        api_client.force_authenticate(user=auth_user)
        response = api_client.delete(
            f"{global_url}{workout_plan_created.id}/{extra_comments_url}{1}/",
            format="json",
        )

        assert response.status_code == 404
        assert (
            str(response.data["detail"]) == "No WorkoutComment matches the given query."
        )

    def test_unauthenticated_user_cannot_delete_comments(
        self, api_client, comment_created
    ):
        workout_plan = comment_created.workout_plan
        response = api_client.delete(
            f"{global_url}{workout_plan.id}/{extra_comments_url}{comment_created.id}/",
            format="json",
        )

        assert response.status_code == 401

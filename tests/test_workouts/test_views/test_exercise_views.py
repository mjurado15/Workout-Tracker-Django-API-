import pytest

from django.urls import reverse


pytestmark = [pytest.mark.integration, pytest.mark.django_db]


class TestListExerciseView:
    url = reverse("exercises-list")

    def test_user_can_access_the_exercises(
        self, api_client, user_created, create_batch_exercises
    ):
        exercises = create_batch_exercises(5)

        api_client.force_authenticate(user=user_created)
        response = api_client.get(self.url, format="json")

        assert response.status_code == 200
        assert len(response.json()) == len(exercises)

        response_exercises = response.json()

        # Check that all exercise ids and names match
        response_names = {
            (exercise["id"], exercise["name"]) for exercise in response_exercises
        }
        expected_names = {(exercise.id, exercise.name) for exercise in exercises}

        assert response_names == expected_names

    def test_unauthenticated_user_cannot_access_exercises(self, api_client):
        response = api_client.get(self.url, format="json")

        assert response.status_code == 401


class TestExerciseViews:
    url = reverse("exercises-list")

    def test_user_can_retrieve_exercise(
        self, api_client, user_created, exercise_created
    ):
        api_client.force_authenticate(user_created)
        response = api_client.get(f"{self.url}{exercise_created.id}/", format="json")

        assert response.status_code == 200
        assert response.json()["id"] == exercise_created.id
        assert response.json()["name"] == exercise_created.name

    def test_user_cannot_retrieve_exercise_that_not_exist(
        self, api_client, user_created
    ):
        api_client.force_authenticate(user_created)
        response = api_client.get(f"{self.url}23/", format="json")

        assert response.status_code == 404

    def test_unauthenticated_user_cannot_retrieve_exercise(self, api_client):
        response = api_client.get(self.url, format="json")

        assert response.status_code == 401

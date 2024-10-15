import pytest

from django.urls import reverse
from rest_framework.test import APIClient

pytestmark = [pytest.mark.integration, pytest.mark.django_db]

client = APIClient()


class TestExerciseViews:
    url = reverse("exercises-list")

    def test_list(self, create_batch_exercises):
        exercises = create_batch_exercises(5)

        response = client.get(self.url, format="json")

        assert response.status_code == 200
        assert len(response.json()) == len(exercises)

        response_exercises = response.json()

        # Check that all exercise ids and names match
        response_names = {
            (exercise["id"], exercise["name"]) for exercise in response_exercises
        }
        expected_names = {(exercise.id, exercise.name) for exercise in exercises}

        assert response_names == expected_names

    def test_retrieve(self, exercise_created):
        response = client.get(f"{self.url}{exercise_created.id}/", format="json")

        assert response.status_code == 200
        assert response.json()["id"] == exercise_created.id
        assert response.json()["name"] == exercise_created.name

    def test_retrieve__not_found_exercise(self):
        response = client.get(f"{self.url}23/", format="json")

        assert response.status_code == 404
        assert "detail" in response.json()

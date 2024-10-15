import pytest

from django.urls import reverse
from rest_framework.test import APIClient

pytestmark = [pytest.mark.integration, pytest.mark.django_db]

client = APIClient()


class TestExerciseCategoryViews:
    url = reverse("exercise-categories-list")

    def test_list(self, create_batch_exercise_categories):
        categories = create_batch_exercise_categories(5)

        response = client.get(self.url, format="json")

        assert response.status_code == 200
        assert len(response.json()) == len(categories)

        response_categories = response.json()

        # Check that all category ids and names match
        response_names = {
            (category["id"], category["name"]) for category in response_categories
        }
        category_names = {(category.id, category.name) for category in categories}

        assert response_names == category_names

    def test_retrieve(self, exercise_category_created):
        response = client.get(
            f"{self.url}{exercise_category_created.id}/", format="json"
        )

        assert response.status_code == 200
        assert response.json() == {
            "id": exercise_category_created.id,
            "name": exercise_category_created.name,
        }

    def test_retrieve__not_found_exercise_category(self):
        response = client.get(f"{self.url}23/", format="json")

        assert response.status_code == 404
        assert "detail" in response.json()

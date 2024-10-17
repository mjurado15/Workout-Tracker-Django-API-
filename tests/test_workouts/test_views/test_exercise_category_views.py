import pytest

from django.urls import reverse

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


class TestListExerciseCategoryView:
    url = reverse("exercise-categories-list")

    def test_user_can_access_the_exercise_categories(
        self, api_client, user_created, create_batch_exercise_categories
    ):
        categories = create_batch_exercise_categories(5)

        api_client.force_authenticate(user=user_created)
        response = api_client.get(self.url, format="json")

        assert response.status_code == 200
        assert set(response.data.keys()) == {"count", "next", "previous", "results"}
        assert len(response.data["results"]) == len(categories)

        response_categories = response.data["results"]

        # Check that all category ids and names match
        response_names = {
            (category["id"], category["name"]) for category in response_categories
        }
        category_names = {(category.id, category.name) for category in categories}

        assert response_names == category_names

    def test_unauthenticated_user_cannot_access_exercise_categories(self, api_client):
        response = api_client.get(self.url, format="json")

        assert response.status_code == 401


class TestRetrieveExerciseCategoryViews:
    url = reverse("exercise-categories-list")

    def test_user_can_retrieve_exercise_category(
        self, api_client, user_created, exercise_category_created
    ):
        api_client.force_authenticate(user=user_created)
        response = api_client.get(
            f"{self.url}{exercise_category_created.id}/", format="json"
        )

        assert response.status_code == 200
        assert response.json() == {
            "id": exercise_category_created.id,
            "name": exercise_category_created.name,
        }

    def test_user_cannot_retrieve_exercise_category_that_not_exist(
        self, api_client, user_created
    ):
        api_client.force_authenticate(user=user_created)
        response = api_client.get(f"{self.url}23/", format="json")
        assert response.status_code == 404

    def test_unauthenticated_user_cannot_retrieve_exercise_category(self, api_client):
        response = api_client.get(f"{self.url}23/", format="json")

        assert response.status_code == 401

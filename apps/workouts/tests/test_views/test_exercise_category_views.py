import pytest
from django.urls import reverse

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


class ParentCategoryViews:
    url = reverse("exercise-categories-list")


class TestExerciseCategoryViews(ParentCategoryViews):
    def test_list_categories_sorted_by_name(
        self, api_client, user_created, create_exercise_category_with
    ):
        category1 = create_exercise_category_with(name="Flexibility")
        category2 = create_exercise_category_with(name="cardio")
        category3 = create_exercise_category_with(name="strength")

        api_client.force_authenticate(user=user_created)
        response = api_client.get(self.url, format="json")

        assert response.status_code == 200
        assert set(response.data.keys()) == {"count", "next", "previous", "results"}

        sorted_categories = [category2, category1, category3]
        expected_categories = [
            {"id": str(category.id), "name": str(category.name)}
            for category in sorted_categories
        ]

        assert response.data["results"] == expected_categories

    def test_unauthenticated_user_cannot_list_categories(self, api_client):
        response = api_client.get(self.url, format="json")
        assert response.status_code == 401


class TestExerciseViews(ParentCategoryViews):
    exercises_url = "exercises/"

    def test_list_exercises_in_category_sorted_by_name(
        self,
        api_client,
        user_created,
        create_batch_exercise_categories,
        create_batch_exercises_with,
        create_exercise_with,
    ):
        [target_category, other_category] = create_batch_exercise_categories(size=2)
        create_batch_exercises_with(size=2, category=other_category)

        target_exercise1 = create_exercise_with(
            name="Running", category=target_category
        )
        target_exercise2 = create_exercise_with(
            name="Burpees", category=target_category
        )
        target_exercise3 = create_exercise_with(name="Rowing", category=target_category)

        api_client.force_authenticate(user=user_created)
        response = api_client.get(
            f"{self.url}{target_category.id}/{self.exercises_url}", format="json"
        )

        assert response.status_code == 200
        assert set(response.data.keys()) == {"count", "next", "previous", "results"}

        returned_exercises = [
            (exercise["id"], exercise["name"]) for exercise in response.data["results"]
        ]
        expected_exercises = [
            (str(target_exercise2.id), target_exercise2.name),
            (str(target_exercise3.id), target_exercise3.name),
            (str(target_exercise1.id), target_exercise1.name),
        ]

        assert returned_exercises == expected_exercises

    def test_cannot_list_exercises_from_category_that_not_exist(
        self, api_client, user_created
    ):
        category_id = 23

        api_client.force_authenticate(user=user_created)
        response = api_client.get(
            f"{self.url}{category_id}/{self.exercises_url}",
            format="json",
        )

        assert response.status_code == 404

    def test_unauthenticated_user_cannot_list_exercises(
        self, api_client, exercise_category_created
    ):
        category_id = str(exercise_category_created.id)
        response = api_client.get(
            f"{self.url}{category_id}/{self.exercises_url}",
            format="json",
        )
        assert response.status_code == 401

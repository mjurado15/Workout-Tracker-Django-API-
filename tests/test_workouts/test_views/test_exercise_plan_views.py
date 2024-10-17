import pytest
from django.urls import reverse

from apps.workouts.models import ExercisePlan


pytestmark = [pytest.mark.integration, pytest.mark.django_db]


class TestListExercisePlanView:
    url = reverse("workout-plans-list")
    extra_url = "exercise_plans/"

    def test_user_can_only_access_the_exercise_plans_of_his_workout_plan(
        self,
        api_client,
        user_created,
        create_batch_workout_plans_with,
        create_batch_exercise_plans_with,
    ):
        [first_workout_plan, second_workout_plan] = create_batch_workout_plans_with(
            size=2,
            user=user_created,
        )
        user_exercise_plans = create_batch_exercise_plans_with(
            size=2, workout_plan=first_workout_plan
        )
        create_batch_exercise_plans_with(size=1, workout_plan=second_workout_plan)

        api_client.force_authenticate(user=user_created)
        response = api_client.get(
            f"{self.url}{first_workout_plan.id}/{self.extra_url}", format="json"
        )

        assert response.status_code == 200
        assert len(response.data) == 2

        response_plans_names = {(item["id"], item["name"]) for item in response.data}
        expected_plans_names = {(item.id, item.name) for item in user_exercise_plans}

        assert response_plans_names == expected_plans_names

    def test_user_cannot_access_the_exercise_plans_of_another_user_s_workout_plan(
        self, api_client, workout_plan_created, user_created
    ):
        api_client.force_authenticate(user=user_created)
        response = api_client.get(
            f"{self.url}{workout_plan_created.id}/{self.extra_url}", format="json"
        )

        assert workout_plan_created.user.id != user_created.id
        assert response.status_code == 404
        assert str(response.data["detail"]) == "No WorkoutPlan matches the given query."

    def test_user_cannot_access_the_exercise_plans_of_workout_plan_that_not_exist(
        self, api_client, user_created
    ):
        api_client.force_authenticate(user=user_created)
        response = api_client.get(f"{self.url}{23}/{self.extra_url}", format="json")

        assert response.status_code == 404
        assert str(response.data["detail"]) == "No WorkoutPlan matches the given query."

    def test_unauthenticated_user_cannot_access_exercise_plans(
        self, api_client, workout_plan_created
    ):
        response = api_client.get(
            f"{self.url}{workout_plan_created.id}/{self.extra_url}", format="json"
        )

        assert response.status_code == 401


class TestCreateExercisePlanView:
    url = reverse("workout-plans-list")
    extra_url = "exercise_plans/"

    def test_user_can_create_an_exercise_plan_for_a_workout_plan(
        self, api_client, workout_plan_created, exercise_created, exercise_plan_built
    ):
        exercise_plan_dict = exercise_plan_built.__dict__
        exercise_plan_dict.pop("_state")
        exercise_plan_dict["exercise"] = exercise_created.id

        api_client.force_authenticate(user=workout_plan_created.user)
        response = api_client.post(
            f"{self.url}{workout_plan_created.id}/{self.extra_url}",
            exercise_plan_dict,
            format="json",
        )

        assert response.status_code == 201
        assert response.data["name"] == exercise_plan_dict["name"]
        assert response.data["description"] == exercise_plan_dict["description"]
        assert response.data["exercise"] == {
            "id": exercise_created.id,
            "name": exercise_created.name,
            "description": exercise_created.description,
            "category": exercise_created.category.name,
        }

        workout_plan_created = ExercisePlan.objects.first()
        assert ExercisePlan.objects.count() == 1
        assert workout_plan_created.name == exercise_plan_dict["name"]
        assert workout_plan_created.description == exercise_plan_dict["description"]

    def test_user_cannot_create_an_exercise_plan_for_another_user_s_workout_plan(
        self, api_client, workout_plan_created, user_created
    ):
        api_client.force_authenticate(user=user_created)
        response = api_client.post(
            f"{self.url}{workout_plan_created.id}/{self.extra_url}", {}, format="json"
        )

        assert user_created.id != workout_plan_created.user.id
        assert response.status_code == 404
        assert str(response.data["detail"]) == "No WorkoutPlan matches the given query."

    def test_user_cannot_create_an_exercise_plan_for_a_non_existent_workout_plan(
        self, api_client, user_created
    ):
        api_client.force_authenticate(user=user_created)
        response = api_client.post(
            f"{self.url}{22}/{self.extra_url}", {}, format="json"
        )

        assert response.status_code == 404
        assert str(response.data["detail"]) == "No WorkoutPlan matches the given query."

    def test_creation_fails_with_incorrect_data(self, api_client, workout_plan_created):
        api_client.force_authenticate(user=workout_plan_created.user)
        response = api_client.post(
            f"{self.url}{workout_plan_created.id}/{self.extra_url}", {}, format="json"
        )

        assert response.status_code == 400
        assert response.data != {}

    def test_unauthenticated_user_cannot_create_workout_plan(
        self, api_client, workout_plan_created
    ):
        response = api_client.post(
            f"{self.url}{workout_plan_created.id}/{self.extra_url}", {}, format="json"
        )
        assert response.status_code == 401


class TestRetrieveExercisePlanView:
    url = reverse("workout-plans-list")
    extra_url = "exercise_plans/"

    def test_user_can_retrieve_exercise_plan_from_his_workout_plans(
        self, api_client, exercise_plan_created
    ):
        workout_plan = exercise_plan_created.workout_plan
        exercise = exercise_plan_created.exercise
        authenticated_user = workout_plan.user

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.get(
            f"{self.url}{workout_plan.id}/{self.extra_url}{exercise_plan_created.id}/",
            format="json",
        )

        assert response.status_code == 200
        assert response.data["name"] == exercise_plan_created.name
        assert response.data["exercise"] == {
            "id": exercise.id,
            "name": exercise.name,
            "description": exercise.description,
            "category": exercise.category.name,
        }

    def test_user_cannot_retrieve_exercise_plan_of_another_user_s_workout_plan(
        self, api_client, user_created, exercise_plan_created
    ):
        workout_plan = exercise_plan_created.workout_plan

        api_client.force_authenticate(user=user_created)
        response = api_client.get(
            f"{self.url}{workout_plan.id}/{self.extra_url}{exercise_plan_created.id}/",
            format="json",
        )

        assert user_created.id != workout_plan.user.id
        assert response.status_code == 404
        assert str(response.data["detail"]) == "No WorkoutPlan matches the given query."

    def test_user_cannot_retrieve_exercise_plan_from_non_existent_workout_plan(
        self, api_client, user_created
    ):
        api_client.force_authenticate(user=user_created)
        response = api_client.get(
            f"{self.url}{2}/{self.extra_url}{1}/",
            format="json",
        )

        assert response.status_code == 404
        assert str(response.data["detail"]) == "No WorkoutPlan matches the given query."

    def test_user_cannot_retrieve_exercise_plan_that_not_exist(
        self, api_client, workout_plan_created
    ):
        api_client.force_authenticate(user=workout_plan_created.user)
        response = api_client.get(
            f"{self.url}{workout_plan_created.id}/{self.extra_url}{1}/",
            format="json",
        )

        assert response.status_code == 404
        assert (
            str(response.data["detail"]) == "No ExercisePlan matches the given query."
        )

    def test_unauthenticated_user_cannot_retrieve_exercise_plan(
        self, api_client, exercise_plan_created
    ):
        workout_plan = exercise_plan_created.workout_plan

        response = api_client.get(
            f"{self.url}{workout_plan.id}/{self.extra_url}{exercise_plan_created.id}/",
            format="json",
        )

        assert response.status_code == 401


class TestUpdateExercisePlanView:

    url = reverse("workout-plans-list")
    extra_url = "exercise_plans/"

    def test_user_can_update_exercise_plan_from_his_workout_plan(
        self, api_client, exercise_plan_created, exercise_plan_built, exercise_created
    ):
        authenticated_user = exercise_plan_created.workout_plan.user
        workout_plan = exercise_plan_created.workout_plan
        old_exercise_plan = exercise_plan_created
        new_exercise_plan_dict = {
            "name": exercise_plan_built.name,
            "description": exercise_plan_built.description,
            "sets": exercise_plan_built.sets,
            "reps": exercise_plan_built.reps,
            "exercise": exercise_created.id,
        }

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.put(
            f"{self.url}{workout_plan.id}/{self.extra_url}{old_exercise_plan.id}/",
            new_exercise_plan_dict,
            format="json",
        )

        assert response.status_code == 200
        assert response.data["name"] == new_exercise_plan_dict["name"]
        assert response.data["description"] == new_exercise_plan_dict["description"]
        assert response.data["sets"] == new_exercise_plan_dict["sets"]
        assert response.data["reps"] == new_exercise_plan_dict["reps"]
        assert response.data["exercise"] == {
            "id": exercise_created.id,
            "name": exercise_created.name,
            "description": exercise_created.description,
            "category": exercise_created.category.name,
        }

    def test_user_cannot_update_exercise_plan_with_incorrect_data(
        self, api_client, exercise_plan_created
    ):
        workout_plan = exercise_plan_created.workout_plan
        authenticated_user = exercise_plan_created.workout_plan.user

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.put(
            f"{self.url}{workout_plan.id}/{self.extra_url}{exercise_plan_created.id}/",
            {},
            format="json",
        )

        assert response.status_code == 400
        assert response.data != {}

    def test_user_cannot_update_exercise_plan_from_another_user_s_workout_plan(
        self, api_client, exercise_plan_created, user_created
    ):
        workout_plan = exercise_plan_created.workout_plan

        api_client.force_authenticate(user=user_created)
        response = api_client.put(
            f"{self.url}{workout_plan.id}/{self.extra_url}{exercise_plan_created.id}/",
            {},
            format="json",
        )

        assert workout_plan.user.id != user_created.id
        assert response.status_code == 404
        assert str(response.data["detail"]) == "No WorkoutPlan matches the given query."

    def test_user_cannot_update_exercise_plan_from_workout_plan_that_not_exist(
        self, api_client, user_created
    ):
        api_client.force_authenticate(user=user_created)
        response = api_client.put(
            f"{self.url}{2}/{self.extra_url}{12}/", {}, format="json"
        )

        assert response.status_code == 404
        assert str(response.data["detail"]) == "No WorkoutPlan matches the given query."

    def test_user_cannot_update_exercise_that_not_exist(
        self, api_client, workout_plan_created
    ):
        authenticated_user = workout_plan_created.user
        api_client.force_authenticate(user=authenticated_user)
        response = api_client.put(
            f"{self.url}{workout_plan_created.id}/{self.extra_url}{12}/",
            {},
            format="json",
        )

        assert response.status_code == 404
        assert (
            str(response.data["detail"]) == "No ExercisePlan matches the given query."
        )

    def test_unauthenticated_user_cannot_update_exercise(
        self, api_client, exercise_plan_created
    ):
        workout_plan = exercise_plan_created.workout_plan

        response = api_client.put(
            f"{self.url}{workout_plan.id}/{self.extra_url}{exercise_plan_created.id}/",
            {},
            format="json",
        )

        assert response.status_code == 401


class TestPartialUpdateExercisePlanView:

    url = reverse("workout-plans-list")
    extra_url = "exercise_plans/"

    @pytest.mark.parametrize(
        "field",
        ["name", "exercise"],
    )
    def test_user_can_partial_update_exercise_plan_from_his_workout_plan(
        self, api_client, exercise_plan_created, exercise_created, field
    ):
        authenticated_user = exercise_plan_created.workout_plan.user
        workout_plan = exercise_plan_created.workout_plan
        old_exercise_plan = exercise_plan_created
        new_exercise_plan = {
            "name": "New exercise plan",
            "exercise": exercise_created.id,
        }
        expected_exercise_plan = {
            **new_exercise_plan,
            "exercise": {
                "id": exercise_created.id,
                "name": exercise_created.name,
                "description": exercise_created.description,
                "category": exercise_created.category.name,
            },
        }

        new_exercise_plan_dict = {
            field: new_exercise_plan[field],
        }

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.patch(
            f"{self.url}{workout_plan.id}/{self.extra_url}{old_exercise_plan.id}/",
            new_exercise_plan_dict,
            format="json",
        )

        assert response.status_code == 200
        assert response.data[field] == expected_exercise_plan[field]

    def test_user_cannot_partial_update_exercise_plan_with_incorrect_data(
        self, api_client, exercise_plan_created
    ):
        workout_plan = exercise_plan_created.workout_plan
        authenticated_user = exercise_plan_created.workout_plan.user
        incorrect_data = {"name": "a" * 151}

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.patch(
            f"{self.url}{workout_plan.id}/{self.extra_url}{exercise_plan_created.id}/",
            incorrect_data,
            format="json",
        )

        assert response.status_code == 400
        assert response.data != {}

    def test_user_cannot_partial_update_exercise_plan_from_another_user_s_workout_plan(
        self, api_client, exercise_plan_created, user_created
    ):
        workout_plan = exercise_plan_created.workout_plan

        api_client.force_authenticate(user=user_created)
        response = api_client.patch(
            f"{self.url}{workout_plan.id}/{self.extra_url}{exercise_plan_created.id}/",
            {},
            format="json",
        )

        assert workout_plan.user.id != user_created.id
        assert response.status_code == 404
        assert str(response.data["detail"]) == "No WorkoutPlan matches the given query."

    def test_user_cannot_partial_update_exercise_plan_from_workout_plan_that_not_exist(
        self, api_client, user_created
    ):
        api_client.force_authenticate(user=user_created)
        response = api_client.patch(
            f"{self.url}{2}/{self.extra_url}{12}/", {}, format="json"
        )

        assert response.status_code == 404
        assert str(response.data["detail"]) == "No WorkoutPlan matches the given query."

    def test_user_cannot_partial_update_exercise_that_not_exist(
        self, api_client, workout_plan_created
    ):
        authenticated_user = workout_plan_created.user
        api_client.force_authenticate(user=authenticated_user)
        response = api_client.patch(
            f"{self.url}{workout_plan_created.id}/{self.extra_url}{12}/",
            {},
            format="json",
        )

        assert response.status_code == 404
        assert (
            str(response.data["detail"]) == "No ExercisePlan matches the given query."
        )

    def test_unauthenticated_user_cannot_partial_update_exercise(
        self, api_client, exercise_plan_created
    ):
        workout_plan = exercise_plan_created.workout_plan

        response = api_client.patch(
            f"{self.url}{workout_plan.id}/{self.extra_url}{exercise_plan_created.id}/",
            {},
            format="json",
        )

        assert response.status_code == 401


class TestDeleteExercisePlanView:
    url = reverse("workout-plans-list")
    extra_url = "exercise_plans/"

    def test_user_can_delete_exercise_plan_from_his_workout_plan(
        self, api_client, exercise_plan_created
    ):
        workout_plan = exercise_plan_created.workout_plan
        authenticated_user = workout_plan.user

        assert ExercisePlan.objects.filter(workout_plan=workout_plan).count() == 1

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.delete(
            f"{self.url}{workout_plan.id}/{self.extra_url}{exercise_plan_created.id}/"
        )

        assert response.status_code == 204
        assert ExercisePlan.objects.filter(workout_plan=workout_plan).count() == 0

    def test_user_cannot_delete_exercise_plan_from_another_user_s_workout_plan(
        self, api_client, exercise_plan_created, user_created
    ):
        workout_plan = exercise_plan_created.workout_plan

        api_client.force_authenticate(user=user_created)
        response = api_client.delete(
            f"{self.url}{workout_plan.id}/{self.extra_url}{exercise_plan_created.id}/"
        )

        assert workout_plan.user.id != user_created.id
        assert response.status_code == 404
        assert str(response.data["detail"]) == "No WorkoutPlan matches the given query."

    def test_user_cannot_delete_exercise_plan_from_workout_plan_that_not_exist(
        self, api_client, user_created
    ):
        api_client.force_authenticate(user=user_created)
        response = api_client.delete(f"{self.url}{2}/{self.extra_url}{1}/")

        assert response.status_code == 404
        assert str(response.data["detail"]) == "No WorkoutPlan matches the given query."

    def test_user_cannot_delete_exercise_plan_that_not_exist(
        self, api_client, workout_plan_created
    ):
        authenticated_user = workout_plan_created.user

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.delete(
            f"{self.url}{workout_plan_created.id}/{self.extra_url}{1}/"
        )

        assert response.status_code == 404
        assert (
            str(response.data["detail"]) == "No ExercisePlan matches the given query."
        )

    def test_unauthenticated_user_cannot_delete_exercise_plan(
        self, api_client, exercise_plan_created
    ):
        workout_plan = exercise_plan_created.workout_plan

        response = api_client.delete(
            f"{self.url}{workout_plan.id}/{self.extra_url}{exercise_plan_created.id}/"
        )

        assert response.status_code == 401

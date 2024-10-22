import uuid

import pytest
from django.urls import reverse

from workouts.models import ExercisePlan
from workouts.serializers import ExerciseSerializer
from workouts.tests.utils import serialize_datetime


pytestmark = [pytest.mark.integration, pytest.mark.django_db]


class ParentExercisePlanView:
    url = reverse("workouts-list")
    exercise_plans_url = "exercise_plans/"

    def create_expected_exercise_plan(self, exercise_plan):
        exercise_plan_dict = {**exercise_plan.__dict__}
        exercise_plan_dict.pop("_state")
        exercise_plan_dict.pop("exercise_id")
        exercise_plan_dict.pop("workout_id")

        exercise_plan_dict["id"] = str(exercise_plan_dict["id"])
        exercise_plan_dict["created_at"] = serialize_datetime(
            exercise_plan_dict["created_at"]
        )
        exercise_plan_dict["updated_at"] = serialize_datetime(
            exercise_plan_dict["updated_at"]
        )

        exercise_plan_dict["exercise"] = ExerciseSerializer(exercise_plan.exercise).data
        exercise_plan_dict["workout"] = str(exercise_plan.workout.id)

        return exercise_plan_dict


class TestListExercisePlanView(ParentExercisePlanView):
    def test_user_can_only_access_exercise_plans_of_their_workout(
        self,
        api_client,
        create_batch_workouts_with,
        create_batch_exercise_plans_with,
        create_exercise_plan_with,
        list_response_keys,
    ):
        [target_workout, other_workout] = create_batch_workouts_with(size=2)
        create_batch_exercise_plans_with(size=2, workout=other_workout)
        exercise_plan_1 = create_exercise_plan_with(
            name="Weighted squats", workout=target_workout
        )
        exercise_plan_2 = create_exercise_plan_with(
            name="intense running", workout=target_workout
        )
        exercise_plan_3 = create_exercise_plan_with(
            name="intense running", workout=target_workout
        )

        authenticated_user = target_workout.user
        workout_id = str(target_workout.id)

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.get(
            f"{self.url}{workout_id}/{self.exercise_plans_url}", format="json"
        )

        assert response.status_code == 200
        assert set(response.data.keys()) == list_response_keys

        sorted_exercise_plans = [exercise_plan_3, exercise_plan_2, exercise_plan_1]
        expected_exercise_plans = [
            self.create_expected_exercise_plan(item) for item in sorted_exercise_plans
        ]

        assert response.json()["results"] == expected_exercise_plans

    def test_user_cannnot_access_exercise_plans_of_another_user_s_workout(
        self,
        api_client,
        workout_created,
        create_batch_exercise_plans_with,
        user_created,
    ):
        target_workout = workout_created
        workout_id = str(target_workout.id)
        create_batch_exercise_plans_with(size=2, workout=target_workout)

        authenticated_user = user_created

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.get(
            f"{self.url}{workout_id}/{self.exercise_plans_url}", format="json"
        )

        assert authenticated_user.id != target_workout.user.id
        assert response.status_code == 404
        assert response.json()["detail"] == "No Workout matches the given query."

    def test_user_cannnot_access_exercise_plans_of_workout_that_not_exist(
        self, api_client, user_created
    ):
        workout_id = uuid.uuid4()
        authenticated_user = user_created

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.get(
            f"{self.url}{workout_id}/{self.exercise_plans_url}", format="json"
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "No Workout matches the given query."

    def test_unauthenticated_user_cannot_access_exercise_plans(
        self, api_client, workout_created
    ):
        workout_id = str(workout_created.id)

        response = response = api_client.get(
            f"{self.url}{workout_id}/{self.exercise_plans_url}", format="json"
        )

        assert response.status_code == 401


class TestRetrieveExercisePlanView(ParentExercisePlanView):
    def test_user_can_access_exercise_plan_of_his_workout(
        self, api_client, exercise_plan_created
    ):
        workout_id = str(exercise_plan_created.workout.id)
        exercise_plan_id = str(exercise_plan_created.id)
        authenticated_user = exercise_plan_created.workout.user

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.get(
            f"{self.url}{workout_id}/{self.exercise_plans_url}{exercise_plan_id}/",
            format="json",
        )

        assert response.status_code == 200
        expected_data = self.create_expected_exercise_plan(exercise_plan_created)

        assert response.json() == expected_data

    def test_user_cannot_access_exercise_plan_that_not_exist(
        self, api_client, workout_created
    ):
        authenticated_user = workout_created.user

        workout_id = str(workout_created.id)
        exercise_plan_id = str(uuid.uuid4())

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.get(
            f"{self.url}{workout_id}/{self.exercise_plans_url}{exercise_plan_id}/",
            format="json",
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "No ExercisePlan matches the given query."

    def test_user_cannot_access_exercise_plan_of_another_user_s_workout(
        self, api_client, user_created, exercise_plan_created
    ):
        authenticated_user = user_created

        workout = exercise_plan_created.workout
        workout_id = str(workout.id)
        exercise_plan_id = str(exercise_plan_created.id)

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.get(
            f"{self.url}{workout_id}/{self.exercise_plans_url}{exercise_plan_id}/",
            format="json",
        )

        assert authenticated_user.id != workout.user.id
        assert response.status_code == 404
        assert response.json()["detail"] == "No Workout matches the given query."

    def test_user_cannot_access_exercise_plan_of_workout_that_not_exist(
        self, api_client, user_created
    ):
        authenticated_user = user_created

        workout_id = str(uuid.uuid4())
        exercise_plan_id = str(uuid.uuid4())

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.get(
            f"{self.url}{workout_id}/{self.exercise_plans_url}{exercise_plan_id}/",
            format="json",
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "No Workout matches the given query."

    def test_unauthenticated_user_cannot_access_exercise_plan(
        self, api_client, exercise_plan_created
    ):
        workout_id = str(exercise_plan_created.workout.id)
        exercise_plan_id = str(exercise_plan_created.id)

        response = api_client.get(
            f"{self.url}{workout_id}/{self.exercise_plans_url}{exercise_plan_id}/",
            format="json",
        )

        assert response.status_code == 401


class TestCreateExercisePlanView(ParentExercisePlanView):
    def test_create_exercise_plan(self, api_client, workout_created, exercise_created):
        authenticated_user = workout_created.user
        workout_id = str(workout_created.id)

        exercise_plan_data = {
            "name": "Test Exercise Plan",
            "description": "This is a test description",
            "exercise": str(exercise_created.id),
        }

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.post(
            f"{self.url}{workout_id}/{self.exercise_plans_url}",
            exercise_plan_data,
            format="json",
        )

        assert response.status_code == 201
        assert ExercisePlan.objects.count() == 1

        plan_created = ExercisePlan.objects.first()
        exercise_plan_data["exercise"] = exercise_created

        assert all(
            getattr(plan_created, field) == exercise_plan_data[field]
            for field in exercise_plan_data
        )
        assert plan_created.workout.user.id == authenticated_user.id

        expected_data = self.create_expected_exercise_plan(plan_created)
        assert response.json() == expected_data

    def test_create_fails_with_incorrect_data(self, api_client, workout_created):
        workout_id = str(workout_created.id)
        authenticated_user = workout_created.user

        exercise_plan_data = {}

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.post(
            f"{self.url}{workout_id}/{self.exercise_plans_url}",
            exercise_plan_data,
            format="json",
        )

        assert response.status_code == 400
        assert ExercisePlan.objects.count() == 0

        assert response.json() != {}

    def test_create_fails_if_workout_not_exist(
        self, api_client, exercise_created, user_created
    ):
        workout_id = str(uuid.uuid4())
        exercise_plan_data = {
            "name": "Test Exercise Plan",
            "description": "This is a test description",
            "exercise": str(exercise_created.id),
        }

        api_client.force_authenticate(user=user_created)
        response = api_client.post(
            f"{self.url}{workout_id}/{self.exercise_plans_url}",
            exercise_plan_data,
            format="json",
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "No Workout matches the given query."

    def test_unauthenticate_user_cannot_create_exercise_plan(
        self, api_client, workout_created
    ):
        workout_id = str(workout_created.id)
        exercise_plan_data = {
            "name": "Test Exercise Plan",
            "description": "This is a test description",
        }

        response = api_client.post(
            f"{self.url}{workout_id}/{self.exercise_plans_url}",
            exercise_plan_data,
            format="json",
        )

        assert response.status_code == 401


class TestPartialUpdateExercisePlanView(ParentExercisePlanView):
    def test_user_can_partial_update_exercise_plan_of_his_workout(
        self, api_client, exercise_plan_created
    ):
        workout = exercise_plan_created.workout
        workout_id = str(workout.id)
        authenticated_user = workout.user

        old_exercise_plan = exercise_plan_created
        exercise_plan_id = str(old_exercise_plan.id)

        new_data = {
            "description": "This is a new test description",
        }

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.patch(
            f"{self.url}{workout_id}/{self.exercise_plans_url}{exercise_plan_id}/",
            new_data,
            format="json",
        )

        assert response.status_code == 200
        plan_updated = ExercisePlan.objects.get(id=old_exercise_plan.id)

        assert all(
            getattr(plan_updated, field) == new_data[field] for field in new_data
        )
        expected_data = self.create_expected_exercise_plan(plan_updated)

        assert response.json() == expected_data

    def test_user_cannot_partial_update_exercise_plan_that_not_exist(
        self, api_client, workout_created
    ):
        workout_id = str(workout_created.id)
        authenticated_user = workout_created.user

        exercise_plan_id = str(uuid.uuid4())

        new_data = {
            "description": "This is a new test description",
        }

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.patch(
            f"{self.url}{workout_id}/{self.exercise_plans_url}{exercise_plan_id}/",
            new_data,
            format="json",
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "No ExercisePlan matches the given query."

    def test_user_cannot_partial_update_exercice_plan_of_another_user_s_workout(
        self, api_client, user_created, exercise_plan_created
    ):
        authenticated_user = user_created

        workout = exercise_plan_created.workout
        workout_id = str(workout.id)

        old_exercise_plan = exercise_plan_created
        exercise_plan_id = str(old_exercise_plan.id)

        new_data = {
            "description": "This is a test description",
        }

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.patch(
            f"{self.url}{workout_id}/{self.exercise_plans_url}{exercise_plan_id}/",
            new_data,
            format="json",
        )

        assert authenticated_user.id != workout.user.id
        assert response.status_code == 404
        assert response.json()["detail"] == "No Workout matches the given query."

    def test_user_cannot_partial_update_exercice_plan_of_workout_that_not_exist(
        self, api_client, user_created
    ):
        authenticated_user = user_created
        workout_id = str(uuid.uuid4())
        exercise_plan_id = str(uuid.uuid4())

        new_data = {
            "description": "This is a test description",
        }

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.patch(
            f"{self.url}{workout_id}/{self.exercise_plans_url}{exercise_plan_id}/",
            new_data,
            format="json",
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "No Workout matches the given query."

    def test_partial_update_exercise_plan_not_fail_with_incomplete_data(
        self, api_client, exercise_plan_created
    ):
        workout = exercise_plan_created.workout
        workout_id = str(workout.id)
        authenticated_user = workout.user

        old_exercise_plan = exercise_plan_created
        exercise_plan_id = str(old_exercise_plan.id)

        new_data = {}

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.patch(
            f"{self.url}{workout_id}/{self.exercise_plans_url}{exercise_plan_id}/",
            new_data,
            format="json",
        )

        assert response.status_code == 200
        updated_plan = ExercisePlan.objects.get(id=old_exercise_plan.id)
        expected_data = self.create_expected_exercise_plan(updated_plan)

        assert response.json() == expected_data

    def test_unauthenticated_user_cannot_partial_update_exercise_plan(
        self, api_client, exercise_plan_created
    ):
        workout = exercise_plan_created.workout
        workout_id = str(workout.id)

        old_exercise_plan = exercise_plan_created
        exercise_plan_id = str(old_exercise_plan.id)

        new_data = {
            "description": "This is a test description",
        }

        response = api_client.patch(
            f"{self.url}{workout_id}/{self.exercise_plans_url}{exercise_plan_id}/",
            new_data,
            format="json",
        )

        assert response.status_code == 401


class TestDeleteExercisePlanView(ParentExercisePlanView):
    def test_user_can_delete_exercise_plan_of_his_workout(
        self, api_client, exercise_plan_created
    ):
        workout = exercise_plan_created.workout
        workout_id = str(workout.id)

        authenticated_user = workout.user

        exercise_plan_id = str(exercise_plan_created.id)

        assert ExercisePlan.objects.count() == 1

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.delete(
            f"{self.url}{workout_id}/{self.exercise_plans_url}{exercise_plan_id}/",
            format="json",
        )

        assert response.status_code == 204
        assert ExercisePlan.objects.count() == 0

    def test_user_cannot_delete_exercise_plan_that_not_exist(
        self, api_client, workout_created
    ):
        authenticated_user = workout_created.user

        workout_id = str(workout_created.id)
        exercise_plan_id = str(uuid.uuid4())

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.delete(
            f"{self.url}{workout_id}/{self.exercise_plans_url}{exercise_plan_id}/",
            format="json",
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "No ExercisePlan matches the given query."

    def test_user_cannot_delete_exercise_plan_of_another_user_s_workout(
        self, api_client, user_created, exercise_plan_created
    ):
        workout = exercise_plan_created.workout
        workout_id = str(workout.id)
        exercise_plan_id = str(exercise_plan_created.id)

        api_client.force_authenticate(user=user_created)
        response = api_client.delete(
            f"{self.url}{workout_id}/{self.exercise_plans_url}{exercise_plan_id}/",
            format="json",
        )

        assert user_created.id != workout.user.id
        assert response.status_code == 404
        assert response.json()["detail"] == "No Workout matches the given query."

    def test_user_cannot_delete_exercise_plan_of_workout_that_not_exist(
        self, api_client, user_created
    ):
        workout_id = str(uuid.uuid4())
        exercise_plan_id = str(uuid.uuid4())

        api_client.force_authenticate(user=user_created)
        response = api_client.delete(
            f"{self.url}{workout_id}/{self.exercise_plans_url}{exercise_plan_id}/",
            format="json",
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "No Workout matches the given query."

    def test_unauthenticated_user_cannot_delete_exercise_plan(
        self, api_client, exercise_plan_created
    ):
        workout = exercise_plan_created.workout
        workout_id = str(workout.id)
        exercise_plan_id = str(exercise_plan_created.id)

        response = response = api_client.delete(
            f"{self.url}{workout_id}/{self.exercise_plans_url}{exercise_plan_id}/",
            format="json",
        )

        assert response.status_code == 401

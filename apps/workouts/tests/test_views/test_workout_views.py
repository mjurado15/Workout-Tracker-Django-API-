import uuid

import pytest
from django.urls import reverse

from workouts.models import Workout
from workouts.tests.utils import serialize_datetime


pytestmark = [pytest.mark.integration, pytest.mark.django_db]


class ParentWorkoutView:
    url = reverse("workouts-list")

    def create_expected_workout(self, workout):
        workout_dict = {
            "id": str(workout.id),
            "name": workout.name,
            "description": workout.description,
            "type": workout.type,
            "status": "Pending",
            "user": str(workout.user.id),
            "created_at": serialize_datetime(workout.created_at),
            "updated_at": serialize_datetime(workout.updated_at),
        }

        return workout_dict


class TestListWorkoutView(ParentWorkoutView):
    def test_user_can_only_access_their_workouts(
        self,
        api_client,
        create_batch_users,
        create_batch_workouts_with,
        create_workout_with,
        list_response_keys,
    ):
        [authenticated_user, other_user] = create_batch_users(size=2)
        create_batch_workouts_with(size=2, user=other_user)

        workout1 = create_workout_with(user=authenticated_user)
        workout2 = create_workout_with(user=authenticated_user)
        workout3 = create_workout_with(user=authenticated_user)

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.get(self.url, format="json")

        assert response.status_code == 200
        assert set(response.data.keys()) == list_response_keys

        sorted_workouts = [workout3, workout2, workout1]
        expected_workouts = [
            self.create_expected_workout(workout) for workout in sorted_workouts
        ]

        assert response.json()["results"] == expected_workouts

    def test_unauthenticated_user_cannot_access_workouts(self, api_client):
        response = api_client.get(self.url, format="json")
        assert response.status_code == 401


class TestRetrieveWorkoutView(ParentWorkoutView):
    def test_user_can_access_his_workout(self, api_client, workout_created):
        authenticated_user = workout_created.user
        workout_id = str(workout_created.id)

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.get(f"{self.url}{workout_id}/", format="json")

        assert response.status_code == 200
        expected_data = self.create_expected_workout(workout_created)

        assert response.json() == expected_data

    def test_user_cannot_access_another_user_s_workout(
        self, api_client, user_created, workout_created
    ):
        workout_id = str(workout_created.id)

        api_client.force_authenticate(user=user_created)
        response = api_client.get(f"{self.url}{workout_id}/", format="json")

        assert user_created != workout_created.user
        assert response.status_code == 404
        assert response.json()["detail"] == "No Workout matches the given query."

    def test_user_cannot_access_workout_that_not_exist(self, api_client, user_created):
        workout_id = str(uuid.uuid4())

        api_client.force_authenticate(user=user_created)
        response = api_client.get(f"{self.url}{workout_id}/", format="json")

        assert response.status_code == 404
        assert response.json()["detail"] == "No Workout matches the given query."

    def test_unauthenticated_user_cannot_access_workout(
        self, api_client, workout_created
    ):
        workout_id = str(workout_created.id)
        response = response = api_client.get(f"{self.url}{workout_id}/", format="json")

        assert response.status_code == 401


class TestCreateWorkoutView(ParentWorkoutView):
    def test_create_workout(self, api_client, user_created):
        workout_data = {
            "name": "Test Workout",
            "description": "This is a test description",
        }
        api_client.force_authenticate(user=user_created)
        response = api_client.post(self.url, workout_data, format="json")

        assert response.status_code == 201
        assert Workout.objects.count() == 1

        workout_created = Workout.objects.first()

        assert all(
            getattr(workout_created, field) == workout_data[field]
            for field in workout_data
        )
        assert workout_created.user == user_created
        expected_data = self.create_expected_workout(workout_created)

        assert response.json() == expected_data

    def test_create_fails_with_incorrect_data(self, api_client, user_created):
        workout_data = {}
        api_client.force_authenticate(user=user_created)
        response = api_client.post(self.url, workout_data, format="json")

        assert response.status_code == 400
        assert Workout.objects.count() == 0

        assert response.json() != {}

    def test_unauthenticate_user_cannot_create_workout(self, api_client):
        workout_data = {
            "name": "Test Workout",
            "description": "This is a test description",
        }
        response = api_client.post(self.url, workout_data, format="json")

        assert response.status_code == 401


class TestUpdateWorkoutView(ParentWorkoutView):
    def test_user_can_update_his_workout(self, api_client, workout_created):
        authenticated_user = workout_created.user

        old_workout = workout_created
        workout_id = str(old_workout.id)

        new_workout_data = {
            "name": "Test Workout",
            "description": "This is a test description",
        }

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.put(
            f"{self.url}{workout_id}/", new_workout_data, format="json"
        )

        assert response.status_code == 200

        old_workout.refresh_from_db()
        assert all(
            getattr(old_workout, field) == new_workout_data[field]
            for field in new_workout_data
        )
        expected_data = self.create_expected_workout(old_workout)

        assert response.json() == expected_data

    def test_user_cannot_update_workout_that_not_exist(self, api_client, user_created):
        authenticated_user = user_created
        workout_id = str(uuid.uuid4())

        new_workout_data = {
            "name": "Test Workout",
            "description": "This is a test description",
        }

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.put(
            f"{self.url}{workout_id}/", new_workout_data, format="json"
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "No Workout matches the given query."

    def test_user_cannot_update_another_user_s_workout(
        self, api_client, user_created, workout_created
    ):
        authenticated_user = user_created

        old_workout = workout_created
        workout_id = str(old_workout.id)

        new_workout_data = {
            "name": "Test Workout",
            "description": "This is a test description",
        }

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.put(
            f"{self.url}{workout_id}/", new_workout_data, format="json"
        )

        assert authenticated_user.id != workout_created.user.id
        assert response.status_code == 404
        assert response.json()["detail"] == "No Workout matches the given query."

    def test_update_workout_fails_with_incomplete_data(
        self, api_client, workout_created
    ):
        authenticated_user = workout_created.user

        old_workout = workout_created
        workout_id = str(old_workout.id)

        new_workout_data = {}

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.put(
            f"{self.url}{workout_id}/", new_workout_data, format="json"
        )

        assert response.status_code == 400
        assert response.json() != {}

    def test_unauthenticated_user_cannot_update_workout(
        self, api_client, workout_created
    ):
        old_workout = workout_created
        workout_id = str(old_workout.id)

        new_workout_data = {
            "name": "Test Workout",
            "description": "This is a test description",
        }

        response = api_client.put(
            f"{self.url}{workout_id}/", new_workout_data, format="json"
        )

        assert response.status_code == 401


class TestPartialUpdateWorkoutView(ParentWorkoutView):
    def test_user_can_partial_update_his_workout(self, api_client, workout_created):
        authenticated_user = workout_created.user

        old_workout = workout_created
        workout_id = str(old_workout.id)

        new_workout_data = {
            "description": "This is a new test description",
        }

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.patch(
            f"{self.url}{workout_id}/", new_workout_data, format="json"
        )

        assert response.status_code == 200

        old_workout.refresh_from_db()
        assert all(
            getattr(old_workout, field) == new_workout_data[field]
            for field in new_workout_data
        )
        expected_data = self.create_expected_workout(old_workout)

        assert response.json() == expected_data

    def test_user_cannot_partial_update_workout_that_not_exist(
        self, api_client, user_created
    ):
        authenticated_user = user_created
        workout_id = str(uuid.uuid4())

        new_workout_data = {
            "description": "This is a test description",
        }

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.patch(
            f"{self.url}{workout_id}/", new_workout_data, format="json"
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "No Workout matches the given query."

    def test_user_cannot_partial_update_another_user_s_workout(
        self, api_client, user_created, workout_created
    ):
        authenticated_user = user_created

        old_workout = workout_created
        workout_id = str(old_workout.id)

        new_workout_data = {
            "description": "This is a test description",
        }

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.patch(
            f"{self.url}{workout_id}/", new_workout_data, format="json"
        )

        assert authenticated_user.id != workout_created.user.id
        assert response.status_code == 404
        assert response.json()["detail"] == "No Workout matches the given query."

    def test_partial_update_workout_not_fail_with_incomplete_data(
        self, api_client, workout_created
    ):
        authenticated_user = workout_created.user

        old_workout = workout_created
        workout_id = str(old_workout.id)

        new_workout_data = {}

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.patch(
            f"{self.url}{workout_id}/", new_workout_data, format="json"
        )

        assert response.status_code == 200

        old_workout.refresh_from_db()
        expected_data = self.create_expected_workout(old_workout)

        assert response.json() == expected_data

    def test_unauthenticated_user_cannot_partial_update_workout(
        self, api_client, workout_created
    ):
        old_workout = workout_created
        workout_id = str(old_workout.id)

        new_workout_data = {
            "description": "This is a test description",
        }

        response = api_client.patch(
            f"{self.url}{workout_id}/", new_workout_data, format="json"
        )

        assert response.status_code == 401


class TestDeleteWorkoutView(ParentWorkoutView):
    def test_user_can_delete_his_workout(self, api_client, workout_created):
        authenticated_user = workout_created.user
        workout_id = str(workout_created.id)

        assert Workout.objects.count() == 1

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.delete(f"{self.url}{workout_id}/", format="json")

        assert response.status_code == 204
        assert Workout.objects.count() == 0

    def test_user_cannot_delete_workout_that_not_exist(self, api_client, user_created):
        workout_id = str(uuid.uuid4())

        api_client.force_authenticate(user=user_created)
        response = api_client.delete(f"{self.url}{workout_id}/", format="json")

        assert response.status_code == 404
        assert response.json()["detail"] == "No Workout matches the given query."

    def test_user_cannot_delete_another_user_s_workout(
        self, api_client, user_created, workout_created
    ):
        workout_id = str(workout_created.id)

        api_client.force_authenticate(user=user_created)
        response = api_client.delete(f"{self.url}{workout_id}/", format="json")

        assert user_created != workout_created.user
        assert response.status_code == 404
        assert response.json()["detail"] == "No Workout matches the given query."

    def test_unauthenticated_user_cannot_delete_workout(
        self, api_client, workout_created
    ):
        workout_id = str(workout_created.id)
        response = response = api_client.delete(
            f"{self.url}{workout_id}/", format="json"
        )

        assert response.status_code == 401

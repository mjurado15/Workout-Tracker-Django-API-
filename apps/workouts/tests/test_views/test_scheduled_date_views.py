import uuid
import datetime

import pytest
from django.urls import reverse

from workouts.models import ScheduledWorkoutDate, Workout


pytestmark = [pytest.mark.integration, pytest.mark.django_db]


class ParentScheduledDateView:
    url = reverse("workouts-list")
    scheduled_dates_url = "scheduled_dates/"

    def create_expected_scheduled_date(self, scheduled_date):
        scheduled_date_dict = {
            "id": str(scheduled_date.id),
            "date": str(scheduled_date.date),
            "time": str(scheduled_date.time),
            "workout": str(scheduled_date.workout.id),
        }

        return scheduled_date_dict


class TestListScheduledDateView(ParentScheduledDateView):
    def test_user_can_only_access_scheduled_dates_of_their_workouts_sorted_by_date_and_time(
        self,
        api_client,
        create_workout_with,
        create_scheduled_date_with,
        list_response_keys,
    ):
        target_workout = create_workout_with(type=Workout.SCHEDULED)
        scheduled1 = create_scheduled_date_with(
            date=datetime.date(2024, 10, 14),
            time=datetime.time(18, 0),
            workout=target_workout,
        )
        scheduled2 = create_scheduled_date_with(
            date=datetime.date(2024, 10, 14),
            time=datetime.time(20, 0),
            workout=target_workout,
        )
        scheduled3 = create_scheduled_date_with(
            date=datetime.date(2024, 10, 12),
            time=datetime.time(21, 0),
            workout=target_workout,
        )

        authenticated_user = target_workout.user
        workout_id = str(target_workout.id)

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.get(
            f"{self.url}{workout_id}/{self.scheduled_dates_url}", format="json"
        )

        assert response.status_code == 200
        assert set(response.data.keys()) == list_response_keys

        sorted_schedulers = [scheduled3, scheduled1, scheduled2]
        expected_schedulers = [
            self.create_expected_scheduled_date(item) for item in sorted_schedulers
        ]

        assert response.json()["results"] == expected_schedulers

    def test_user_cannot_access_scheduled_dates_of_an_unscheduled_workout(
        self, api_client, create_workout_with
    ):
        target_workout = create_workout_with(type=Workout.RECURRENT)

        authenticated_user = target_workout.user
        workout_id = str(target_workout.id)

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.get(
            f"{self.url}{workout_id}/{self.scheduled_dates_url}", format="json"
        )

        assert response.status_code == 412
        assert response.json()["detail"] == "The workout is not scheduled."

    def test_user_cannnot_access_scheduled_dates_of_another_user_s_workout(
        self,
        api_client,
        workout_created,
        create_batch_scheduled_dates_with,
        user_created,
    ):
        target_workout = workout_created
        workout_id = str(target_workout.id)
        create_batch_scheduled_dates_with(size=3, workout=target_workout)

        authenticated_user = user_created

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.get(
            f"{self.url}{workout_id}/{self.scheduled_dates_url}", format="json"
        )

        assert authenticated_user.id != target_workout.user.id
        assert response.status_code == 404
        assert response.json()["detail"] == "No Workout matches the given query."

    def test_user_cannnot_access_scheduled_dates_of_workout_that_not_exist(
        self, api_client, user_created
    ):
        workout_id = uuid.uuid4()
        authenticated_user = user_created

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.get(
            f"{self.url}{workout_id}/{self.scheduled_dates_url}", format="json"
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "No Workout matches the given query."

    def test_unauthenticated_user_cannot_access_scheduled_date(
        self, api_client, workout_created
    ):
        workout_id = str(workout_created.id)

        response = response = api_client.get(
            f"{self.url}{workout_id}/{self.scheduled_dates_url}", format="json"
        )

        assert response.status_code == 401


class TestCreateScheduledDateView(ParentScheduledDateView):
    def test_create_scheduled_date_for_scheduled_type_workout(
        self, api_client, workout_created, scheduled_date_built
    ):
        authenticated_user = workout_created.user
        workout_id = str(workout_created.id)

        scheduled_date_data = {
            "date": scheduled_date_built.date,
            "time": scheduled_date_built.time,
        }

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.post(
            f"{self.url}{workout_id}/{self.scheduled_dates_url}",
            scheduled_date_data,
            format="json",
        )

        assert response.status_code == 201
        assert ScheduledWorkoutDate.objects.count() == 1
        scheduled_created = ScheduledWorkoutDate.objects.first()

        assert scheduled_created.workout.is_scheduled()
        assert all(
            getattr(scheduled_created, field) == scheduled_date_data[field]
            for field in scheduled_date_data
        )

        expected_data = self.create_expected_scheduled_date(scheduled_created)
        assert response.json() == expected_data

    def test_create_scheduled_date_for_an_unscheduled_workout(
        self, api_client, create_workout_with, scheduled_date_built
    ):
        target_workout = create_workout_with(type=Workout.RECURRENT)
        workout_id = str(target_workout.id)

        authenticated_user = target_workout.user

        scheduled_date_data = {
            "date": scheduled_date_built.date,
            "time": scheduled_date_built.time,
        }

        assert not target_workout.is_scheduled()

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.post(
            f"{self.url}{workout_id}/{self.scheduled_dates_url}",
            scheduled_date_data,
            format="json",
        )

        assert response.status_code == 201
        assert ScheduledWorkoutDate.objects.count() == 1
        scheduled_created = ScheduledWorkoutDate.objects.first()

        assert scheduled_created.workout.is_scheduled()
        assert all(
            getattr(scheduled_created, field) == scheduled_date_data[field]
            for field in scheduled_date_data
        )

        expected_data = self.create_expected_scheduled_date(scheduled_created)
        assert response.json() == expected_data

    def test_create_fails_with_incorrect_data(self, api_client, workout_created):
        workout_id = str(workout_created.id)
        authenticated_user = workout_created.user

        scheduled_date_data = {}

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.post(
            f"{self.url}{workout_id}/{self.scheduled_dates_url}",
            scheduled_date_data,
            format="json",
        )

        assert response.status_code == 400
        assert ScheduledWorkoutDate.objects.count() == 0
        assert response.json() != {}

    def test_create_fails_if_workout_not_exist(self, api_client, user_created):
        workout_id = str(uuid.uuid4())
        scheduled_date_data = {}

        api_client.force_authenticate(user=user_created)
        response = api_client.post(
            f"{self.url}{workout_id}/{self.scheduled_dates_url}",
            scheduled_date_data,
            format="json",
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "No Workout matches the given query."

    def test_unauthenticate_user_cannot_create_scheduled_date(
        self, api_client, workout_created, scheduled_date_built
    ):
        workout_id = str(workout_created.id)
        scheduled_date_data = {
            "date": scheduled_date_built.date,
            "time": scheduled_date_built.time,
        }

        response = api_client.post(
            f"{self.url}{workout_id}/{self.scheduled_dates_url}",
            scheduled_date_data,
            format="json",
        )
        assert response.status_code == 401


class TestRetrieveScheduledDateView(ParentScheduledDateView):
    def test_user_can_access_scheduled_date_of_his_workout(
        self, api_client, scheduled_date_created
    ):
        workout = scheduled_date_created.workout
        workout_id = str(workout.id)
        scheduled_date_id = str(scheduled_date_created.id)

        authenticated_user = workout.user

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.get(
            f"{self.url}{workout_id}/{self.scheduled_dates_url}{scheduled_date_id}/",
            format="json",
        )

        assert response.status_code == 200
        expected_data = self.create_expected_scheduled_date(scheduled_date_created)

        assert response.json() == expected_data

    def test_user_cannot_access_scheduled_date_that_not_exist(
        self, api_client, workout_created
    ):
        authenticated_user = workout_created.user

        workout_id = str(workout_created.id)
        scheduled_date_id = str(uuid.uuid4())

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.get(
            f"{self.url}{workout_id}/{self.scheduled_dates_url}{scheduled_date_id}/",
            format="json",
        )

        assert response.status_code == 404
        assert (
            response.json()["detail"]
            == "No ScheduledWorkoutDate matches the given query."
        )

    def test_user_cannot_access_scheduled_date_of_another_user_s_workout(
        self, api_client, user_created, scheduled_date_created
    ):
        authenticated_user = user_created

        workout = scheduled_date_created.workout
        workout_id = str(workout.id)
        scheduled_date_id = str(scheduled_date_created.id)

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.get(
            f"{self.url}{workout_id}/{self.scheduled_dates_url}{scheduled_date_id}/",
            format="json",
        )

        assert authenticated_user.id != workout.user.id
        assert response.status_code == 404
        assert response.json()["detail"] == "No Workout matches the given query."

    def test_user_cannot_access_scheduled_date_of_workout_that_not_exist(
        self, api_client, user_created
    ):
        authenticated_user = user_created

        workout_id = str(uuid.uuid4())
        scheduled_date_id = str(uuid.uuid4())

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.get(
            f"{self.url}{workout_id}/{self.scheduled_dates_url}{scheduled_date_id}/",
            format="json",
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "No Workout matches the given query."

    def test_unauthenticated_user_cannot_access_scheduled_date(
        self, api_client, scheduled_date_created
    ):
        workout_id = str(scheduled_date_created.workout.id)
        scheduled_date_id = str(scheduled_date_created.id)

        response = api_client.get(
            f"{self.url}{workout_id}/{self.scheduled_dates_url}{scheduled_date_id}/",
            format="json",
        )

        assert response.status_code == 401


class TestPartialUpdateScheduledDateView(ParentScheduledDateView):
    def test_user_can_partial_update_scheduled_date_of_his_workout(
        self, api_client, scheduled_date_created, scheduled_date_built
    ):
        workout = scheduled_date_created.workout
        workout_id = str(workout.id)
        authenticated_user = workout.user

        old_scheduled_date = scheduled_date_created
        scheduled_date_id = str(old_scheduled_date.id)

        new_data = {
            "date": scheduled_date_built.date,
        }

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.patch(
            f"{self.url}{workout_id}/{self.scheduled_dates_url}{scheduled_date_id}/",
            new_data,
            format="json",
        )

        assert response.status_code == 200
        updated_scheduled_date = ScheduledWorkoutDate.objects.get(
            id=old_scheduled_date.id
        )

        assert all(
            getattr(updated_scheduled_date, field) == new_data[field]
            for field in new_data
        )
        expected_data = self.create_expected_scheduled_date(updated_scheduled_date)

        assert response.json() == expected_data

    def test_user_cannot_partial_update_scheduled_date_that_not_exist(
        self, api_client, workout_created, scheduled_date_built
    ):
        workout_id = str(workout_created.id)
        authenticated_user = workout_created.user

        scheduled_date_id = str(uuid.uuid4())

        new_data = {
            "date": scheduled_date_built.date,
        }

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.patch(
            f"{self.url}{workout_id}/{self.scheduled_dates_url}{scheduled_date_id}/",
            new_data,
            format="json",
        )

        assert response.status_code == 404
        assert (
            response.json()["detail"]
            == "No ScheduledWorkoutDate matches the given query."
        )

    def test_user_cannot_partial_update_scheduled_date_of_another_user_s_workout(
        self, api_client, user_created, scheduled_date_created, scheduled_date_built
    ):
        authenticated_user = user_created

        workout = scheduled_date_created.workout
        workout_id = str(workout.id)

        old_scheduled_date = scheduled_date_created
        scheduled_date_id = str(old_scheduled_date.id)

        new_data = {
            "date": scheduled_date_built.date,
        }

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.patch(
            f"{self.url}{workout_id}/{self.scheduled_dates_url}{scheduled_date_id}/",
            new_data,
            format="json",
        )

        assert authenticated_user.id != workout.user.id
        assert response.status_code == 404
        assert response.json()["detail"] == "No Workout matches the given query."

    def test_user_cannot_partial_update_scheduled_date_of_workout_that_not_exist(
        self, api_client, user_created, scheduled_date_built
    ):
        authenticated_user = user_created
        workout_id = str(uuid.uuid4())
        scheduled_date_id = str(uuid.uuid4())

        new_data = {
            "date": scheduled_date_built.date,
        }

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.patch(
            f"{self.url}{workout_id}/{self.scheduled_dates_url}{scheduled_date_id}/",
            new_data,
            format="json",
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "No Workout matches the given query."

    def test_partial_update_scheduled_date_not_fail_with_incomplete_data(
        self, api_client, scheduled_date_created
    ):
        workout = scheduled_date_created.workout
        workout_id = str(workout.id)
        authenticated_user = workout.user

        old_scheduled_date = scheduled_date_created
        scheduled_date_id = str(old_scheduled_date.id)

        new_data = {}

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.patch(
            f"{self.url}{workout_id}/{self.scheduled_dates_url}{scheduled_date_id}/",
            new_data,
            format="json",
        )

        assert response.status_code == 200
        updated_scheduled_date = ScheduledWorkoutDate.objects.get(
            id=old_scheduled_date.id
        )
        expected_data = self.create_expected_scheduled_date(updated_scheduled_date)

        assert response.json() == expected_data

    def test_unauthenticated_user_cannot_partial_update_scheduled_date(
        self, api_client, scheduled_date_created, scheduled_date_built
    ):
        workout = scheduled_date_created.workout
        workout_id = str(workout.id)

        old_scheduled_date = scheduled_date_created
        scheduled_date_id = str(old_scheduled_date.id)

        new_data = {
            "date": scheduled_date_built.date,
        }

        response = api_client.patch(
            f"{self.url}{workout_id}/{self.scheduled_dates_url}{scheduled_date_id}/",
            new_data,
            format="json",
        )

        assert response.status_code == 401


class TestDeleteScheduledDateView(ParentScheduledDateView):
    def test_user_can_delete_scheduled_date_of_his_workout(
        self, api_client, scheduled_date_created
    ):
        workout = scheduled_date_created.workout
        workout_id = str(workout.id)

        authenticated_user = workout.user

        scheduled_date_id = str(scheduled_date_created.id)

        assert ScheduledWorkoutDate.objects.count() == 1

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.delete(
            f"{self.url}{workout_id}/{self.scheduled_dates_url}{scheduled_date_id}/",
            format="json",
        )

        assert response.status_code == 204
        assert ScheduledWorkoutDate.objects.count() == 0

    def test_user_cannot_delete_scheduled_date_that_not_exist(
        self, api_client, workout_created
    ):
        authenticated_user = workout_created.user

        workout_id = str(workout_created.id)
        scheduled_date_id = str(uuid.uuid4())

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.delete(
            f"{self.url}{workout_id}/{self.scheduled_dates_url}{scheduled_date_id}/",
            format="json",
        )

        assert response.status_code == 404
        assert (
            response.json()["detail"]
            == "No ScheduledWorkoutDate matches the given query."
        )

    def test_user_cannot_delete_scheduled_date_of_another_user_s_workout(
        self, api_client, user_created, scheduled_date_created
    ):
        workout = scheduled_date_created.workout
        workout_id = str(workout.id)
        scheduled_date_id = str(scheduled_date_created.id)

        api_client.force_authenticate(user=user_created)
        response = api_client.delete(
            f"{self.url}{workout_id}/{self.scheduled_dates_url}{scheduled_date_id}/",
            format="json",
        )

        assert user_created.id != workout.user.id
        assert response.status_code == 404
        assert response.json()["detail"] == "No Workout matches the given query."

    def test_user_cannot_delete_scheduled_date_of_workout_that_not_exist(
        self, api_client, user_created
    ):
        workout_id = str(uuid.uuid4())
        scheduled_date_id = str(uuid.uuid4())

        api_client.force_authenticate(user=user_created)
        response = api_client.delete(
            f"{self.url}{workout_id}/{self.scheduled_dates_url}{scheduled_date_id}/",
            format="json",
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "No Workout matches the given query."

    def test_unauthenticated_user_cannot_delete_scheduled_dates(
        self, api_client, scheduled_date_created
    ):
        workout = scheduled_date_created.workout
        workout_id = str(workout.id)
        scheduled_date_id = str(scheduled_date_created.id)

        response = response = api_client.delete(
            f"{self.url}{workout_id}/{self.scheduled_dates_url}{scheduled_date_id}/",
            format="json",
        )

        assert response.status_code == 401

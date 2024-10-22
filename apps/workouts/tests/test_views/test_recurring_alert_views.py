import uuid
import datetime

import pytest
from django.urls import reverse

from workouts.models import RecurringWorkoutAlert, Workout


pytestmark = [pytest.mark.integration, pytest.mark.django_db]


class ParentRecurringAlertView:
    url = reverse("workouts-list")
    recurring_alerts_url = "recurring_alerts/"

    def create_expected_alert(self, alert):
        alert_dict = {
            "id": str(alert.id),
            "time": str(alert.time),
            "week_days": alert.week_days,
            "workout": str(alert.workout.id),
        }

        return alert_dict


class TestListRecurringAlertView(ParentRecurringAlertView):
    def test_user_can_only_access_alerts_of_their_workouts_sorted_by_time(
        self,
        api_client,
        create_workout_with,
        create_recurring_alert_with,
        list_response_keys,
    ):
        target_workout = create_workout_with(type=Workout.RECURRENT)
        alert1 = create_recurring_alert_with(
            time=datetime.time(18, 0), workout=target_workout
        )
        alert2 = create_recurring_alert_with(
            time=datetime.time(20, 0), workout=target_workout
        )
        alert3 = create_recurring_alert_with(
            time=datetime.time(17, 0), workout=target_workout
        )

        authenticated_user = target_workout.user
        workout_id = str(target_workout.id)

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.get(
            f"{self.url}{workout_id}/{self.recurring_alerts_url}", format="json"
        )

        assert response.status_code == 200
        assert set(response.data.keys()) == list_response_keys

        sorted_alerts = [alert3, alert1, alert2]
        expected_schedulers = [
            self.create_expected_alert(item) for item in sorted_alerts
        ]

        assert response.json()["results"] == expected_schedulers

    def test_user_cannot_access_alerts_of_a_non_recurring_workout(
        self, api_client, create_workout_with
    ):
        target_workout = create_workout_with(type=Workout.SCHEDULED)

        authenticated_user = target_workout.user
        workout_id = str(target_workout.id)

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.get(
            f"{self.url}{workout_id}/{self.recurring_alerts_url}", format="json"
        )

        assert response.status_code == 412
        assert response.json()["detail"] == "The workout is not recurrent."

    def test_user_cannnot_access_alerts_of_another_user_s_workout(
        self, api_client, workout_created, user_created
    ):
        target_workout = workout_created
        workout_id = str(target_workout.id)

        authenticated_user = user_created

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.get(
            f"{self.url}{workout_id}/{self.recurring_alerts_url}", format="json"
        )

        assert authenticated_user.id != target_workout.user.id
        assert response.status_code == 404
        assert response.json()["detail"] == "No Workout matches the given query."

    def test_user_cannnot_access_alerts_of_workout_that_not_exist(
        self, api_client, user_created
    ):
        workout_id = uuid.uuid4()
        authenticated_user = user_created

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.get(
            f"{self.url}{workout_id}/{self.recurring_alerts_url}", format="json"
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "No Workout matches the given query."

    def test_unauthenticated_user_cannot_access_alerts(
        self, api_client, workout_created
    ):
        workout_id = str(workout_created.id)

        response = response = api_client.get(
            f"{self.url}{workout_id}/{self.recurring_alerts_url}", format="json"
        )

        assert response.status_code == 401


class TestCreateRecurringAlertView(ParentRecurringAlertView):
    def test_create_alert_for_recurring_type_workout(
        self, api_client, workout_created, recurring_alert_built
    ):
        authenticated_user = workout_created.user
        workout_id = str(workout_created.id)

        alert_data = {
            "time": recurring_alert_built.time,
            "week_days": recurring_alert_built.week_days,
        }

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.post(
            f"{self.url}{workout_id}/{self.recurring_alerts_url}",
            alert_data,
            format="json",
        )

        assert response.status_code == 201
        assert RecurringWorkoutAlert.objects.count() == 1
        alert_created = RecurringWorkoutAlert.objects.first()

        assert alert_created.workout.is_recurrent()
        assert all(
            getattr(alert_created, field) == alert_data[field] for field in alert_data
        )

        expected_data = self.create_expected_alert(alert_created)
        assert response.json() == expected_data

    def test_create_alert_for_a_non_recurring_workout(
        self, api_client, create_workout_with, recurring_alert_built
    ):
        target_workout = create_workout_with(type=Workout.SCHEDULED)
        workout_id = str(target_workout.id)

        authenticated_user = target_workout.user

        alert_data = {
            "time": recurring_alert_built.time,
            "week_days": recurring_alert_built.week_days,
        }

        assert not target_workout.is_recurrent()

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.post(
            f"{self.url}{workout_id}/{self.recurring_alerts_url}",
            alert_data,
            format="json",
        )

        assert response.status_code == 201
        assert RecurringWorkoutAlert.objects.count() == 1
        alert_created = RecurringWorkoutAlert.objects.first()

        assert alert_created.workout.is_recurrent()
        assert all(
            getattr(alert_created, field) == alert_data[field] for field in alert_data
        )

        expected_data = self.create_expected_alert(alert_created)
        assert response.json() == expected_data

    def test_create_fails_with_incorrect_data(self, api_client, workout_created):
        workout_id = str(workout_created.id)
        authenticated_user = workout_created.user

        alert_data = {}

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.post(
            f"{self.url}{workout_id}/{self.recurring_alerts_url}",
            alert_data,
            format="json",
        )

        assert response.status_code == 400
        assert RecurringWorkoutAlert.objects.count() == 0
        assert response.json() != {}

    def test_create_fails_if_workout_not_exist(self, api_client, user_created):
        workout_id = str(uuid.uuid4())
        alert_data = {}

        api_client.force_authenticate(user=user_created)
        response = api_client.post(
            f"{self.url}{workout_id}/{self.recurring_alerts_url}",
            alert_data,
            format="json",
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "No Workout matches the given query."

    def test_unauthenticate_user_cannot_create_alert(
        self, api_client, workout_created, recurring_alert_built
    ):
        workout_id = str(workout_created.id)
        alert_data = {
            "time": recurring_alert_built.time,
            "week_days": recurring_alert_built.week_days,
        }

        response = api_client.post(
            f"{self.url}{workout_id}/{self.recurring_alerts_url}",
            alert_data,
            format="json",
        )
        assert response.status_code == 401


class TestRetrieveRecurringAlertView(ParentRecurringAlertView):
    def test_user_can_access_alert_of_his_workout(
        self, api_client, recurring_alert_created
    ):
        workout = recurring_alert_created.workout
        workout_id = str(workout.id)
        alert_id = str(recurring_alert_created.id)

        authenticated_user = workout.user

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.get(
            f"{self.url}{workout_id}/{self.recurring_alerts_url}{alert_id}/",
            format="json",
        )

        assert response.status_code == 200
        expected_data = self.create_expected_alert(recurring_alert_created)

        assert response.json() == expected_data

    def test_user_cannot_access_alert_that_not_exist(self, api_client, workout_created):
        authenticated_user = workout_created.user

        workout_id = str(workout_created.id)
        alert_id = str(uuid.uuid4())

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.get(
            f"{self.url}{workout_id}/{self.recurring_alerts_url}{alert_id}/",
            format="json",
        )

        assert response.status_code == 404
        assert (
            response.json()["detail"]
            == "No RecurringWorkoutAlert matches the given query."
        )

    def test_user_cannot_access_alert_of_another_user_s_workout(
        self, api_client, user_created, recurring_alert_created
    ):
        authenticated_user = user_created

        workout = recurring_alert_created.workout
        workout_id = str(workout.id)
        alert_id = str(recurring_alert_created.id)

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.get(
            f"{self.url}{workout_id}/{self.recurring_alerts_url}{alert_id}/",
            format="json",
        )

        assert authenticated_user.id != workout.user.id
        assert response.status_code == 404
        assert response.json()["detail"] == "No Workout matches the given query."

    def test_user_cannot_access_alert_of_workout_that_not_exist(
        self, api_client, user_created
    ):
        authenticated_user = user_created

        workout_id = str(uuid.uuid4())
        alert_id = str(uuid.uuid4())

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.get(
            f"{self.url}{workout_id}/{self.recurring_alerts_url}{alert_id}/",
            format="json",
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "No Workout matches the given query."

    def test_unauthenticated_user_cannot_access_alert(
        self, api_client, recurring_alert_created
    ):
        workout_id = str(recurring_alert_created.workout.id)
        alert_id = str(recurring_alert_created.id)

        response = api_client.get(
            f"{self.url}{workout_id}/{self.recurring_alerts_url}{alert_id}/",
            format="json",
        )

        assert response.status_code == 401


class TestPartialUpdateRecurringAlertView(ParentRecurringAlertView):
    def test_user_can_partial_update_alert_of_his_workout(
        self, api_client, recurring_alert_created, recurring_alert_built
    ):
        workout = recurring_alert_created.workout
        workout_id = str(workout.id)
        authenticated_user = workout.user

        old_alert = recurring_alert_created
        alert_id = str(old_alert.id)

        new_data = {"time": recurring_alert_built.time}

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.patch(
            f"{self.url}{workout_id}/{self.recurring_alerts_url}{alert_id}/",
            new_data,
            format="json",
        )

        assert response.status_code == 200
        updated_alert = RecurringWorkoutAlert.objects.get(id=old_alert.id)

        assert all(
            getattr(updated_alert, field) == new_data[field] for field in new_data
        )
        expected_data = self.create_expected_alert(updated_alert)

        assert response.json() == expected_data

    def test_user_cannot_partial_update_alert_that_not_exist(
        self, api_client, workout_created, recurring_alert_built
    ):
        workout_id = str(workout_created.id)
        authenticated_user = workout_created.user

        alert_id = str(uuid.uuid4())

        new_data = {"time": recurring_alert_built.time}

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.patch(
            f"{self.url}{workout_id}/{self.recurring_alerts_url}{alert_id}/",
            new_data,
            format="json",
        )

        assert response.status_code == 404
        assert (
            response.json()["detail"]
            == "No RecurringWorkoutAlert matches the given query."
        )

    def test_user_cannot_partial_update_alert_of_another_user_s_workout(
        self, api_client, user_created, recurring_alert_created, recurring_alert_built
    ):
        authenticated_user = user_created

        workout = recurring_alert_created.workout
        workout_id = str(workout.id)

        old_alert = recurring_alert_created
        alert_id = str(old_alert.id)

        new_data = {"time": recurring_alert_built.time}

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.patch(
            f"{self.url}{workout_id}/{self.recurring_alerts_url}{alert_id}/",
            new_data,
            format="json",
        )

        assert authenticated_user.id != workout.user.id
        assert response.status_code == 404
        assert response.json()["detail"] == "No Workout matches the given query."

    def test_user_cannot_partial_update_alert_of_workout_that_not_exist(
        self, api_client, user_created, recurring_alert_built
    ):
        authenticated_user = user_created
        workout_id = str(uuid.uuid4())
        alert_id = str(uuid.uuid4())

        new_data = {"time": recurring_alert_built.time}

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.patch(
            f"{self.url}{workout_id}/{self.recurring_alerts_url}{alert_id}/",
            new_data,
            format="json",
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "No Workout matches the given query."

    def test_partial_update_alert_not_fail_with_incomplete_data(
        self, api_client, recurring_alert_created
    ):
        workout = recurring_alert_created.workout
        workout_id = str(workout.id)
        authenticated_user = workout.user

        old_alert = recurring_alert_created
        alert_id = str(old_alert.id)

        new_data = {}

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.patch(
            f"{self.url}{workout_id}/{self.recurring_alerts_url}{alert_id}/",
            new_data,
            format="json",
        )

        assert response.status_code == 200
        updated_alert = RecurringWorkoutAlert.objects.get(id=old_alert.id)
        expected_data = self.create_expected_alert(updated_alert)

        assert response.json() == expected_data

    def test_unauthenticated_user_cannot_partial_update_alert(
        self, api_client, recurring_alert_created, recurring_alert_built
    ):
        workout = recurring_alert_created.workout
        workout_id = str(workout.id)

        old_alert = recurring_alert_created
        alert_id = str(old_alert.id)

        new_data = {"time": recurring_alert_built.time}

        response = api_client.patch(
            f"{self.url}{workout_id}/{self.recurring_alerts_url}{alert_id}/",
            new_data,
            format="json",
        )

        assert response.status_code == 401


class TestDeleteRecurringAlertView(ParentRecurringAlertView):
    def test_user_can_delete_alert_of_his_workout(
        self, api_client, recurring_alert_created
    ):
        workout = recurring_alert_created.workout
        workout_id = str(workout.id)

        authenticated_user = workout.user

        alert_id = str(recurring_alert_created.id)

        assert RecurringWorkoutAlert.objects.count() == 1

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.delete(
            f"{self.url}{workout_id}/{self.recurring_alerts_url}{alert_id}/",
            format="json",
        )

        assert response.status_code == 204
        assert RecurringWorkoutAlert.objects.count() == 0

    def test_user_cannot_delete_alert_that_not_exist(self, api_client, workout_created):
        authenticated_user = workout_created.user

        workout_id = str(workout_created.id)
        alert_id = str(uuid.uuid4())

        api_client.force_authenticate(user=authenticated_user)
        response = api_client.delete(
            f"{self.url}{workout_id}/{self.recurring_alerts_url}{alert_id}/",
            format="json",
        )

        assert response.status_code == 404
        assert (
            response.json()["detail"]
            == "No RecurringWorkoutAlert matches the given query."
        )

    def test_user_cannot_delete_alert_of_another_user_s_workout(
        self, api_client, user_created, recurring_alert_created
    ):
        workout = recurring_alert_created.workout
        workout_id = str(workout.id)
        alert_id = str(recurring_alert_created.id)

        api_client.force_authenticate(user=user_created)
        response = api_client.delete(
            f"{self.url}{workout_id}/{self.recurring_alerts_url}{alert_id}/",
            format="json",
        )

        assert user_created.id != workout.user.id
        assert response.status_code == 404
        assert response.json()["detail"] == "No Workout matches the given query."

    def test_user_cannot_delete_alert_of_workout_that_not_exist(
        self, api_client, user_created
    ):
        workout_id = str(uuid.uuid4())
        alert_id = str(uuid.uuid4())

        api_client.force_authenticate(user=user_created)
        response = api_client.delete(
            f"{self.url}{workout_id}/{self.recurring_alerts_url}{alert_id}/",
            format="json",
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "No Workout matches the given query."

    def test_unauthenticated_user_cannot_delete_alerts(
        self, api_client, recurring_alert_created
    ):
        workout = recurring_alert_created.workout
        workout_id = str(workout.id)
        alert_id = str(recurring_alert_created.id)

        response = response = api_client.delete(
            f"{self.url}{workout_id}/{self.recurring_alerts_url}{alert_id}/",
            format="json",
        )

        assert response.status_code == 401

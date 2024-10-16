import pytest

from django.urls import reverse

from apps.workouts.models import WorkoutPlan


pytestmark = [pytest.mark.integration, pytest.mark.django_db]


class TestListWorkoutPlanView:
    url = reverse("workout-plans-list")

    def test_user_can_only_access_their_own_workout_plans(
        self, api_client, create_batch_workout_plans_with, create_batch_users
    ):
        [user_authenticated, other_user] = create_batch_users(size=2)
        user_workout_plans = create_batch_workout_plans_with(
            size=3, user=user_authenticated
        )
        create_batch_workout_plans_with(size=2, user=other_user)

        api_client.force_authenticate(user=user_authenticated)
        response = api_client.get(self.url, format="json")

        assert response.status_code == 200
        assert len(response.data) == 3

        response_plans_names = {(item["id"], item["name"]) for item in response.data}
        expected_plans_names = {(item.id, item.name) for item in user_workout_plans}

        assert response_plans_names == expected_plans_names

    def test_workout_plans_are_ordered_by_created_at_and_id_in_descending_order(
        self, api_client, user_created, create_batch_workout_plans_with
    ):
        workout_plan1 = create_batch_workout_plans_with(size=1, user=user_created)[0]
        workout_plan2 = create_batch_workout_plans_with(size=1, user=user_created)[0]

        api_client.force_authenticate(user=user_created)
        response = api_client.get(self.url, format="json")

        assert response.status_code == 200
        ids = [plan["id"] for plan in response.data]

        assert ids == [workout_plan2.id, workout_plan1.id]

    def test_unauthenticated_user_cannot_access_workout_plans(self, api_client):
        response = api_client.get(self.url, format="json")
        assert response.status_code == 401


class TestRetriveWorkoutPlanView:
    url = reverse("workout-plans-list")

    def test_user_can_retrieve_workout_plan_of_his_own(
        self, api_client, create_batch_workout_plans_with
    ):
        [workout_plan] = create_batch_workout_plans_with(size=1)

        api_client.force_authenticate(user=workout_plan.user)
        response = api_client.get(f"{self.url}{workout_plan.id}/", format="json")

        assert response.status_code == 200
        assert response.json()["id"] == workout_plan.id
        assert response.json()["name"] == workout_plan.name

    def test_user_cannot_retrieve_workout_plan_that_not_exist(
        self, api_client, user_created
    ):
        api_client.force_authenticate(user=user_created)
        response = api_client.get(f"{self.url}1/", format="json")
        assert response.status_code == 404

    def test_retrieve_cannot_retrieve_another_user_s_workout_plan(
        self, api_client, user_created, create_batch_workout_plans_with
    ):
        workout_plan = create_batch_workout_plans_with(size=1)[0]

        api_client.force_authenticate(user=user_created)
        response = api_client.get(f"{self.url}{workout_plan.id}/", format="json")

        assert user_created.id != workout_plan.user.id
        assert response.status_code == 404

    def test_unauthenticated_user_cannot_retrieve_workout_plan(self, api_client):
        response = api_client.get(f"{self.url}12/", format="json")
        assert response.status_code == 401


class TestCreateWorkoutPlanView:
    url = reverse("workout-plans-list")

    def test_user_can_create_workout_plan(self, api_client, workout_plan_built):
        user = workout_plan_built.user
        user.save()

        workout_plan_data = {**workout_plan_built.__dict__}
        workout_plan_data.pop("id")
        workout_plan_data.pop("_state")

        api_client.force_authenticate(user)
        response = api_client.post(self.url, workout_plan_data, format="json")

        assert response.status_code == 201

        workout_plan_response = response.json()
        assert workout_plan_response["name"] == workout_plan_data["name"]
        assert workout_plan_response["description"] == workout_plan_data["description"]

        workout_plan_created = WorkoutPlan.objects.first()
        assert WorkoutPlan.objects.count() == 1
        assert workout_plan_created.name == workout_plan_data["name"]
        assert workout_plan_created.description == workout_plan_data["description"]

    def test_creation_fails_with_incorrect_data(self, api_client, user_created):
        api_client.force_authenticate(user_created)
        response = api_client.post(self.url, {}, format="json")

        assert response.status_code == 400
        assert response.json() != {}

    def test_unauthenticated_user_cannot_create_workout_plan(self, api_client):
        response = api_client.post(self.url, {}, format="json")

        assert response.status_code == 401


class TestUpdateWorkoutPlanView:
    url = reverse("workout-plans-list")

    def test_user_can_update_workout_plan_of_his_own(
        self,
        api_client,
        create_batch_workout_plans_with,
        user_created,
        workout_plan_built,
    ):
        old_workout_plan = create_batch_workout_plans_with(size=1, user=user_created)[0]
        new_workout_plan_dict = {
            "name": workout_plan_built.name,
            "description": workout_plan_built.description,
        }

        api_client.force_authenticate(user_created)
        response = api_client.put(
            f"{self.url}{old_workout_plan.id}/", new_workout_plan_dict, format="json"
        )

        assert response.status_code == 200

        workout_plan_updated = response.json()
        assert workout_plan_updated["name"] == new_workout_plan_dict["name"]
        assert (
            workout_plan_updated["description"] == new_workout_plan_dict["description"]
        )

    def test_update_fails_with_incorrect_data(
        self, api_client, create_batch_workout_plans_with, user_created
    ):
        old_workout_plan = create_batch_workout_plans_with(size=1, user=user_created)[0]

        api_client.force_authenticate(user_created)
        response = api_client.put(
            f"{self.url}{old_workout_plan.id}/", {}, format="json"
        )

        assert response.status_code == 400
        assert response.json() != {}

    def test_user_cannot_update_workout_plan_that_not_exist(
        self, api_client, user_created
    ):
        api_client.force_authenticate(user_created)
        response = api_client.put(f"{self.url}10/", {}, format="json")

        assert response.status_code == 404

    def test_user_cannot_update_another_user_s_workout_plan(
        self, api_client, user_created, create_batch_workout_plans_with
    ):
        workout_plan = create_batch_workout_plans_with(size=1)[0]

        api_client.force_authenticate(user_created)
        response = api_client.put(f"{self.url}{workout_plan.id}/", {}, format="json")

        assert user_created.id != workout_plan.user.id
        assert response.status_code == 404

    def test_unauthenticated_user_cannot_update_workout_plan(self, api_client):
        response = api_client.post(f"{self.url}10/", {}, format="json")
        assert response.status_code == 401


class TestPartialUpdateWorkoutPlanView:
    url = reverse("workout-plans-list")

    @pytest.mark.parametrize(
        "field",
        [
            "name",
            "description",
        ],
    )
    def test_user_can_partial_update_workout_plan_of_his_own(
        self,
        api_client,
        create_batch_workout_plans_with,
        user_created,
        workout_plan_built,
        field,
    ):
        old_workout_plan = create_batch_workout_plans_with(size=1, user=user_created)[0]
        new_workout_plan_dict = {
            field: getattr(workout_plan_built, field),
        }

        api_client.force_authenticate(user_created)
        response = api_client.patch(
            f"{self.url}{old_workout_plan.id}/", new_workout_plan_dict, format="json"
        )

        assert response.status_code == 200

        workout_plan_updated = response.json()
        assert workout_plan_updated[field] == new_workout_plan_dict[field]

    def test_user_cannot_partial_update_workout_plan_that_not_exist(
        self, api_client, user_created
    ):
        api_client.force_authenticate(user_created)
        response = api_client.patch(f"{self.url}10/", {}, format="json")

        assert response.status_code == 404

    def test_user_cannot_partial_update_another_user_s_workout_plan(
        self, api_client, user_created, create_batch_workout_plans_with
    ):
        workout_plan = create_batch_workout_plans_with(size=1)[0]

        api_client.force_authenticate(user_created)
        response = api_client.patch(f"{self.url}{workout_plan.id}/", {}, format="json")

        assert user_created.id != workout_plan.user.id
        assert response.status_code == 404

    def test_unauthenticated_user_cannot_partial_update_workout_plan(self, api_client):
        response = api_client.patch(f"{self.url}10/", {}, format="json")
        assert response.status_code == 401


class TestDeleteWorkoutPlanViews:
    url = reverse("workout-plans-list")

    def test_user_can_delete_workout_plan_of_this_own(
        self, api_client, create_batch_workout_plans_with
    ):
        workout_plan = create_batch_workout_plans_with(size=1)[0]
        user = workout_plan.user

        assert WorkoutPlan.objects.filter(user=user).count() == 1

        api_client.force_authenticate(user)
        response = api_client.delete(f"{self.url}{workout_plan.id}/", format="json")

        assert response.status_code == 204
        assert WorkoutPlan.objects.filter(user=user).count() == 0

    def test_user_cannot_delete_workout_plan_that_not_exist(
        self, api_client, user_created
    ):
        api_client.force_authenticate(user_created)
        response = api_client.delete(f"{self.url}1/", {}, format="json")

        assert response.status_code == 404

    def test_user_cannot_delete_another_user_s_workout_plan(
        self, api_client, user_created, create_batch_workout_plans_with
    ):
        workout_plan = create_batch_workout_plans_with(size=1)[0]

        api_client.force_authenticate(user_created)
        response = api_client.delete(f"{self.url}{workout_plan.id}/", {}, format="json")

        assert user_created.id != workout_plan.user.id
        assert response.status_code == 404

    def test_unauthenticated_user_cannot_delete_workout_plan(self, api_client):
        response = api_client.delete(f"{self.url}1/", format="json")
        assert response.status_code == 401

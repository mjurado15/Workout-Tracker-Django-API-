import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.users.models import User
from apps.users.serializers import TokenObtainPairSerializer

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

client = APIClient()


class TestSignupView:
    url = reverse("signup")

    def test_signup_successful(self, user_built):
        response = client.post(self.url, user_built, format="json")
        assert response.status_code == 201
        assert User.objects.count() == 1

        user_created = User.objects.first()
        assert user_created.email == user_built["email"]
        assert user_created.first_name == user_built["first_name"]
        assert user_created.last_name == user_built["last_name"]

        assert response.json() == {
            "id": user_created.id,
            "email": user_built["email"],
            "first_name": user_built["first_name"],
            "last_name": user_built["last_name"],
        }

    def test_signup_failed_with_incorrect_data(self):
        response = client.post(self.url, {}, format="json")
        assert response.status_code == 400
        assert response.json() != {}

    def test_signup_failed_with_existing_email(self, user_created, user_built):
        user_data = {**user_built, "email": user_created.email}
        response = client.post(self.url, user_data, format="json")

        assert response.status_code == 400
        assert set(response.json().keys()) == {"email"}
        assert response.json()["email"][0] == "A user with that email already exists."


class TestLoginView:
    url = reverse("login")

    def test_login_successful(self, create_user_with):
        user = create_user_with(password="password1234")
        access_data = {"email": user.email, "password": "password1234"}
        response = client.post(self.url, access_data, format="json")

        assert response.status_code == 200
        response_data = response.json()

        assert set(response_data.keys()) == {"access", "refresh", "user"}
        assert response_data["user"] == {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }

    def test_login_failed_with_invalid_credentials(self):
        access_data = {"email": "test@test.com", "password": "test_password"}
        response = client.post(self.url, access_data, format="json")

        assert response.status_code == 401
        assert response.json() == {
            "detail": "No active account found with the given credentials"
        }

    def test_login_failed_for_an_inactive_user(self, create_user_with):
        user = create_user_with(password="password1234", is_active=False)
        access_data = {"email": user.email, "password": "password1234"}
        response = client.post(self.url, access_data, format="json")

        assert response.status_code == 401
        assert response.json() == {
            "detail": "No active account found with the given credentials"
        }

    def test_login_failed_with_incorrect_data(self):
        access_data = {}
        response = client.post(self.url, access_data, format="json")

        assert response.status_code == 400
        assert set(response.json().keys()) == {"email", "password"}


class TestRefreshTokenView:
    url = reverse("refresh-token")

    def test_refresh_token_successful(self, create_user_with):
        user = create_user_with(password="password1234")
        access_data = {"email": user.email, "password": "password1234"}
        serializer = TokenObtainPairSerializer(data=access_data)
        serializer.is_valid()
        refresh_token = serializer.validated_data["refresh"]

        response = client.post(self.url, {"refresh": refresh_token}, format="json")

        assert response.status_code == 200
        assert set(response.json().keys()) == {"access", "refresh"}

    def test_refresh_token_failed_with_incorrect_data(self):
        response = client.post(self.url, {}, format="json")

        assert response.status_code == 400
        assert set(response.json().keys()) == {"refresh"}
        assert response.json()["refresh"][0] == "This field is required."

    @pytest.mark.parametrize("refresh_token", ["", None])
    def test_refresh_token_failed_with_empty_token(self, refresh_token):
        data = {"refresh": refresh_token}
        response = client.post(self.url, data, format="json")

        assert response.status_code == 400
        assert set(response.json().keys()) == {"refresh"}

    def test_refresh_token_failed_with_invalid_token(self):
        response = client.post(self.url, {"refresh": "invalid_token"}, format="json")
        assert response.status_code == 401

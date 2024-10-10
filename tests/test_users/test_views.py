import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.users.models import User
from apps.users.serializers import TokenObtainPairSerializer

pytestmark = pytest.mark.django_db

client = APIClient()


class TestSignupView:
    url = reverse("signup")

    def test_signup_successful(self, user_built):
        response = client.post(self.url, user_built, format="json")
        assert response.status_code == 201

        all_users = User.objects.all()
        user = all_users.first()
        assert all_users.count() == 1
        assert user.email == user_built["email"]
        assert user.first_name == user_built["first_name"]
        assert user.last_name == user_built["last_name"]

    def test_signup_failed_with_incorrect_data(self):
        response = client.post(self.url, {}, format="json")
        assert response.status_code == 400
        assert response.json() != {}

    def test_signup_failed_with_existing_email(self, user_created, user_built):
        user_data = {**user_built, "email": user_created.email}
        response = client.post(self.url, user_data, format="json")

        assert response.status_code == 400
        assert "email" in response.json()
        assert response.json()["email"][0] == "A user with that email already exists."


class TestLoginView:
    url = reverse("login")

    def test_login_successful(self, create_user_with):
        user = create_user_with(password="password1234")
        access_data = {"email": user.email, "password": "password1234"}
        response = client.post(self.url, access_data, format="json")

        assert response.status_code == 200
        response_data = response.json()
        assert "access" in response_data
        assert "refresh" in response_data
        assert "user" in response_data
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
        assert response.json() != {}
        assert "email" in response.json()
        assert "password" in response.json()


class TestRefreshTokenview:
    url = reverse("refresh-token")

    def test_refresh_token_successful(self, create_user_with):
        user = create_user_with(password="password1234")
        access_data = {"email": user.email, "password": "password1234"}
        serializer = TokenObtainPairSerializer(data=access_data)
        serializer.is_valid()
        refresh_token = serializer.validated_data["refresh"]

        response = client.post(self.url, {"refresh": refresh_token}, format="json")
        assert response.status_code == 200
        assert "access" in response.json()
        assert "refresh" in response.json()

    @pytest.mark.parametrize(
        "token_data, expected",
        [
            ({}, {"status": 400, "message": "This field is required."}),
            (
                {"refresh": None},
                {"status": 400, "message": "This field may not be null."},
            ),
            (
                {"refresh": ""},
                {"status": 400, "message": "This field may not be blank."},
            ),
        ],
    )
    def test_refresh_token_failed_with_incorrect_data(self, token_data, expected):
        response = client.post(self.url, token_data, format="json")
        assert response.status_code == expected["status"]
        assert "refresh" in response.json()
        assert response.json()["refresh"][0] == expected["message"]

    def test_refresh_token_failed_with_invalid_token(self):
        response = client.post(self.url, {"refresh": "invalid_token"}, format="json")
        assert response.status_code == 401

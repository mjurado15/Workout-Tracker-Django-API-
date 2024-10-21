import pytest
from django.urls import reverse

from users.serializers import TokenObtainPairSerializer


pytestmark = [pytest.mark.integration, pytest.mark.django_db]


class TestSignupView:
    url = reverse("signup")

    def test_signup(self, api_client, user_built):
        user_data = user_built.__dict__
        user_data.pop("_state")

        response = api_client.post(self.url, user_data, format="json")
        expected_data = {
            "email": user_data["email"],
            "first_name": user_data["first_name"],
            "last_name": user_data["last_name"],
        }

        assert response.status_code == 201
        response_data = response.data
        response_data.pop("id")

        assert response_data == expected_data

    def test_signup_failed(self, api_client):
        user_data = {}
        response = api_client.post(self.url, user_data, format="json")

        assert response.status_code == 400
        assert response.data != {}


class TestLoginView:
    url = reverse("login")

    def test_login(self, api_client, create_user_with):
        user_password = "super_secure_password"
        user_created = create_user_with(password=user_password)
        credentials = {"email": user_created.email, "password": user_password}

        response = api_client.post(self.url, credentials, format="json")

        assert response.status_code == 200
        assert set(response.data.keys()) == {"access", "refresh", "user"}
        assert response.data["user"] == {
            "id": str(user_created.id),
            "email": user_created.email,
            "first_name": user_created.first_name,
            "last_name": user_created.last_name,
        }

    def test_login_failed_with_invalid_credentials(self, api_client):
        invalid_credentials = {"email": "test@gmail.com", "password": "invaid_password"}
        response = api_client.post(self.url, invalid_credentials, format="json")

        assert response.status_code == 401

    def test_login_failed_with_incorrect_data(self, api_client):
        bad_credentials = {}
        response = api_client.post(self.url, bad_credentials, format="json")

        assert response.status_code == 400
        assert "email" in response.data
        assert "password" in response.data


class TestRefreshTokenView:
    url = reverse("refresh-token")

    @pytest.fixture(autouse=True)
    def set_refresh_token(self, create_user_with):
        user_password = "super_secret_pw"
        user_created = create_user_with(password=user_password)
        credentials = {"email": user_created.email, "password": user_password}
        serializer = TokenObtainPairSerializer(data=credentials)
        serializer.is_valid()
        self.refresh_token = serializer.validated_data["refresh"]

    def test_refresh_token(self, api_client):
        refresh_data = {
            "refresh": self.refresh_token,
        }

        response = api_client.post(self.url, refresh_data, format="json")

        assert response.status_code == 200
        assert set(response.data.keys()) == {"access", "refresh"}

    def test_refresh_token_failed_with_bad_data(self, api_client):
        refresh_data = {}

        response = api_client.post(self.url, refresh_data, format="json")

        assert response.status_code == 400
        assert set(response.data.keys()) == {"refresh"}

    def test_refresh_token_failed_with_invalid_token(self, api_client):
        refresh_data = {
            "refresh": "invalid token",
        }
        response = api_client.post(self.url, refresh_data, format="json")

        assert response.status_code == 401

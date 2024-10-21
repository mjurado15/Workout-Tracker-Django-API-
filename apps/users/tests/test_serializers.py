import uuid

import pytest
from django_mock_queries.query import MockModel
from rest_framework.exceptions import AuthenticationFailed

from users.serializers import (
    UserSerializer,
    SignupSerializer,
    TokenObtainPairSerializer,
)


pytestmark = [pytest.mark.unit]


class TestUserSerializer:
    @pytest.fixture(autouse=True)
    def mock_exists(self, mocker):
        mocker.patch("django.db.models.query.QuerySet.exists", return_value=False)

    def test_serialize_model(self, user_built):
        user_data = {
            "id": uuid.uuid4(),
            "email": user_built.email,
            "first_name": user_built.first_name,
            "last_name": user_built.last_name,
        }
        user = MockModel(**user_data)
        serializer = UserSerializer(user)

        expected_data = {**user_data, "id": str(user_data["id"])}

        assert serializer.data == expected_data

    def test_valid_data(self, user_built):
        user_data = {
            "email": user_built.email,
            "first_name": user_built.first_name,
            "last_name": user_built.last_name,
        }
        serializer = UserSerializer(data=user_data)

        assert serializer.is_valid()
        assert set(serializer.validated_data) == {"email", "first_name", "last_name"}

    def test_invalid_data(self):
        user_data = {}
        serializer = UserSerializer(data=user_data)

        assert not serializer.is_valid()
        assert serializer.errors != {}

    def test_ignore_extra_fields(self, user_built):
        user_data = {
            "email": user_built.email,
            "first_name": user_built.first_name,
            "last_name": user_built.last_name,
            "extra_field": "extra value",
        }
        serializer = UserSerializer(data=user_data)

        assert serializer.is_valid()
        assert "extra_field" not in serializer.validated_data


class TestSignupSerializer:
    @pytest.fixture(autouse=True)
    def mock_exists(self, mocker):
        mocker.patch("django.db.models.query.QuerySet.exists", return_value=False)

    def test_serialize_model(self, user_built):
        user_data = {
            "id": uuid.uuid4(),
            "email": user_built.email,
            "first_name": user_built.first_name,
            "last_name": user_built.last_name,
        }
        user = MockModel(**user_data)
        serializer = SignupSerializer(user)

        expected_data = {**user_data, "id": str(user_data["id"])}

        assert serializer.data == expected_data

    def test_valid_data(self, user_built):
        user_data = {
            "email": user_built.email,
            "first_name": user_built.first_name,
            "last_name": user_built.last_name,
            "password": user_built.password,
        }
        serializer = SignupSerializer(data=user_data)

        assert serializer.is_valid()
        assert set(serializer.validated_data) == {
            "email",
            "first_name",
            "last_name",
            "password",
        }

    def test_ignore_extra_fields(self, user_built):
        user_data = {
            "email": user_built.email,
            "first_name": user_built.first_name,
            "last_name": user_built.last_name,
            "password": user_built.password,
            "extra_field": "extra value",
        }
        serializer = SignupSerializer(data=user_data)

        assert serializer.is_valid()
        assert "extra_field" not in serializer.validated_data

    def test_invalid_data(self):
        user_data = {}
        serializer = SignupSerializer(data=user_data)

        assert not serializer.is_valid()
        assert serializer.errors != {}

    def test_passwork_with_less_than_8_characters_are_not_valid(self, user_built):
        user_data = {
            "email": user_built.email,
            "first_name": user_built.first_name,
            "last_name": user_built.last_name,
            "password": "short",
        }
        serializer = SignupSerializer(data=user_data)

        assert not serializer.is_valid()
        assert (
            str(serializer.errors["password"][0])
            == "Ensure this field has at least 8 characters."
        )


class TestTokenObtainPairSerializer:
    @pytest.fixture(autouse=True)
    def mock_authenticate(self, mocker):
        self.mocked_authenticate = mocker.patch(
            "rest_framework_simplejwt.serializers.authenticate", return_value=None
        )

    def test_invalid_credentials_raises_error(self):
        self.mocked_authenticate.return_value = None

        invalid_credentials = {"email": "test@gmail.com", "password": "test_password"}
        serializer = TokenObtainPairSerializer(data=invalid_credentials)

        with pytest.raises(AuthenticationFailed):
            serializer.is_valid()

    def test_inactive_user_raises_error(self):
        inactive_user = MockModel(id=1, is_active=False)
        self.mocked_authenticate.return_value = inactive_user

        credentials = {"email": "test@gmail.com", "password": "test_password"}
        serializer = TokenObtainPairSerializer(data=credentials)

        with pytest.raises(AuthenticationFailed):
            serializer.is_valid()

    def test_valid_user__return_access_tokens_and_user_data(self, user_built):
        user_data = {
            "email": user_built.email,
            "first_name": user_built.first_name,
            "last_name": user_built.last_name,
        }
        active_user = MockModel(**user_data, is_active=True)

        self.mocked_authenticate.return_value = active_user

        credentials = {"email": user_data["email"], "password": "test_password"}
        serializer = TokenObtainPairSerializer(data=credentials)
        serializer.is_valid()

        assert "access" in serializer.validated_data
        assert "refresh" in serializer.validated_data
        assert "user" in serializer.validated_data
        assert serializer.validated_data["user"] == user_data

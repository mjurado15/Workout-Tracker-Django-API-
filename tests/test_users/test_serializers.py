import pytest
from .factories import UserFactory
from rest_framework.exceptions import AuthenticationFailed

from apps.users.serializers import (
    UserSerializer,
    SignupSerializer,
    TokenObtainPairSerializer,
)


pytestmark = pytest.mark.django_db


class TestUserSerializer:
    def test_serialize_model(self, user_created):
        serializer = UserSerializer(user_created)
        assert serializer.data == {
            "id": user_created.id,
            "email": user_created.email,
            "first_name": user_created.first_name,
            "last_name": user_created.last_name,
        }

    def test_serializer_valid_data(self, user_built):
        serializer = UserSerializer(data=user_built)
        assert serializer.is_valid()
        assert serializer.errors == {}

    def test_serializer_exclude_disallowed_fields(self, user_built):
        input_data = {
            **user_built,
            "extra_field": "extra_value",
        }
        serializer = UserSerializer(data=input_data)
        assert serializer.is_valid()
        assert "extra_field" not in serializer.validated_data

    def test_serializer_invalid_data(self):
        invalid_data = {}
        serializer = UserSerializer(data=invalid_data)
        assert not serializer.is_valid()
        assert serializer.errors != {}


class TestSignupSerializer:
    def test_serializer_valid_data(self, build_user_with):
        data = build_user_with(password="password1234")
        serializer = SignupSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.errors == {}

    def test_serializer_exclude_disallowed_fields(self, user_built):
        input_data = {
            **user_built,
            "extra_field": "extra_value",
        }
        serializer = SignupSerializer(data=input_data)
        assert serializer.is_valid()
        assert "extra_field" not in serializer.validated_data

    def test_serializer_invalid_data(self):
        invalid_data = {}
        serializer = SignupSerializer(data=invalid_data)
        assert not serializer.is_valid()
        assert serializer.errors != {}

    def test_password_with_less_than_8_characters_are_not_valid(self, build_user_with):
        data = build_user_with(password="test")
        serializer = SignupSerializer(data=data)
        assert not serializer.is_valid()
        assert "password" in serializer.errors
        assert (
            str(serializer.errors["password"][0])
            == "Ensure this field has at least 8 characters."
        )


class TestTokenObtainPairSerializer:
    def test_generate_access_tokens_and_return_user_data(self, create_user_with):
        user = create_user_with(password="password123")
        access_data = {"email": user.email, "password": "password123"}
        serializer = TokenObtainPairSerializer(data=access_data)

        assert serializer.is_valid()
        assert "access" in serializer.validated_data
        assert "refresh" in serializer.validated_data
        assert serializer.validated_data["user"] == {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }

    def test_invalid_user_raises_authentication_error(self):
        access_data = {"email": "test@test.com", "password": "password123"}
        serializer = TokenObtainPairSerializer(data=access_data)
        with pytest.raises(AuthenticationFailed) as excinfo:
            serializer.is_valid()

        assert (
            str(excinfo.value) == "No active account found with the given credentials"
        )

    def test_inactive_user_raises_authentication_error(self, create_user_with):
        user = create_user_with(password="password123", is_active=False)
        access_data = {"email": user.email, "password": "password123"}
        serializer = TokenObtainPairSerializer(data=access_data)
        with pytest.raises(AuthenticationFailed) as excinfo:
            serializer.is_valid()

        assert not user.is_active
        assert (
            str(excinfo.value) == "No active account found with the given credentials"
        )

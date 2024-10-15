import pytest
from rest_framework.exceptions import AuthenticationFailed
from django_mock_queries.query import MockModel

from apps.users.serializers import (
    UserSerializer,
    SignupSerializer,
    TokenObtainPairSerializer,
)


pytestmark = [pytest.mark.unit]


class TestUserSerializer:
    @pytest.fixture(autouse=True)
    def mock_exists(self, mocker):
        self.exists_mock = mocker.patch(
            "django.db.models.query.QuerySet.exists", return_value=False
        )

    def test_serialize_model(self, user_built):
        user = MockModel(id=1, **user_built)
        serializer = UserSerializer(user)
        assert serializer.data == {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }

    def test_serializer_valid_data(self, user_built):
        user_built.pop("password")
        serializer = UserSerializer(data=user_built)
        assert serializer.is_valid()
        assert serializer.errors == {}

    def test_serializer_ignore_extra_fields(self, user_built):
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
        assert set(serializer.errors) == {"email", "first_name", "last_name"}


class TestSignupSerializer:
    @pytest.fixture(autouse=True)
    def mock_exists(self, mocker):
        self.exists_mock = mocker.patch(
            "django.db.models.query.QuerySet.exists", return_value=False
        )

    def test_serializer_model(self, user_built):
        user = MockModel(id=1, **user_built)
        serializer = SignupSerializer(user)

        assert serializer.data == {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }

    def test_serializer_valid_data(self, user_built):
        serializer = SignupSerializer(data=user_built)
        assert serializer.is_valid()
        assert serializer.errors == {}

    def test_serializer_ignore_extra_fields(self, user_built):
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
        assert set(serializer.errors) == {
            "email",
            "first_name",
            "last_name",
            "password",
        }

    def test_unique_email(self, user_built):
        self.exists_mock.return_value = True

        serializer = SignupSerializer(data=user_built)
        assert not serializer.is_valid()
        assert "email" in serializer.errors
        assert (
            str(serializer.errors["email"][0])
            == "A user with that email already exists."
        )

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
    @pytest.fixture(autouse=True)
    def mock_authenticate(self, mocker):
        self.authenticate_mock = mocker.patch(
            "rest_framework_simplejwt.serializers.authenticate"
        )

    def test_invalid_user_raises_authentication_error(self):
        self.authenticate_mock.return_value = None

        access_data = {"email": "test@test.com", "password": "password123"}
        serializer = TokenObtainPairSerializer(data=access_data)

        with pytest.raises(AuthenticationFailed) as excinfo:
            serializer.is_valid()
        assert (
            str(excinfo.value) == "No active account found with the given credentials"
        )

    def test_inactive_user_raises_authentication_error(self, user_built):
        inactive_user = MockModel(id=1, is_active=False, **user_built)
        self.authenticate_mock.return_value = inactive_user
        access_data = {
            "email": user_built["email"],
            "password": user_built["password"],
        }
        serializer = TokenObtainPairSerializer(data=access_data)

        with pytest.raises(AuthenticationFailed) as excinfo:
            serializer.is_valid()

        assert not inactive_user.is_active
        assert (
            str(excinfo.value) == "No active account found with the given credentials"
        )

    def test_return_access_tokens_and_user_data(self, user_built):
        user = MockModel(id=1, is_active=True, **user_built)
        self.authenticate_mock.return_value = user

        access_data = {
            "email": user_built["email"],
            "password": user_built["password"],
        }
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

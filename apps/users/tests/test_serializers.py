import uuid

import pytest
from django_mock_queries.query import MockModel
from rest_framework.exceptions import AuthenticationFailed

from users.serializers import UserSerializer, RegisterSerializer


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
            "first_name": user_built.first_name,
            "last_name": user_built.last_name,
        }
        serializer = UserSerializer(data=user_data)

        assert serializer.is_valid()
        assert set(serializer.validated_data) == {"first_name", "last_name"}

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


class TestRegisterSerializer:
    @pytest.fixture(autouse=True)
    def mock_exists(self, mocker):
        mocker.patch("django.db.models.query.QuerySet.exists", return_value=False)

    def test_serialize_model(self, user_built):
        user_data = {
            "email": user_built.email,
            "first_name": user_built.first_name,
            "last_name": user_built.last_name,
        }
        user = MockModel(**user_data)
        serializer = RegisterSerializer(user)

        assert serializer.data == user_data

    def test_valid_data(self, user_built):
        user_data = {
            "email": user_built.email,
            "first_name": user_built.first_name,
            "last_name": user_built.last_name,
            "password1": user_built.password,
            "password2": user_built.password,
        }
        serializer = RegisterSerializer(data=user_data)

        assert serializer.is_valid()
        assert set(serializer.validated_data) == set(user_data.keys())

    def test_ignore_extra_fields(self, user_built):
        user_data = {
            "email": user_built.email,
            "first_name": user_built.first_name,
            "last_name": user_built.last_name,
            "password1": user_built.password,
            "password2": user_built.password,
            "extra_field": "extra value",
        }
        serializer = RegisterSerializer(data=user_data)

        assert serializer.is_valid()
        assert "extra_field" not in serializer.validated_data

    def test_invalid_data(self):
        user_data = {}
        serializer = RegisterSerializer(data=user_data)

        assert not serializer.is_valid()
        assert serializer.errors != {}

    def test_get_cleaned_data(self, user_built):
        user_data = {
            "email": user_built.email,
            "first_name": user_built.first_name,
            "last_name": user_built.last_name,
            "password1": user_built.password,
            "password2": user_built.password,
        }
        serializer = RegisterSerializer(data=user_data)
        serializer.is_valid()
        user_data.pop("password2")

        assert serializer.get_cleaned_data() == user_data

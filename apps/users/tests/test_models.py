import pytest
from django.utils import timezone
from django.db.utils import IntegrityError

from users.models import User


pytestmark = [pytest.mark.unit, pytest.mark.django_db]


class TestUserModel:
    def test_create_user_with_required_fields(self, user_built):
        user_data = {
            "first_name": user_built.first_name,
            "last_name": user_built.last_name,
            "email": user_built.email,
            "password": user_built.password,
        }

        user = User.objects.create_user(**user_data)

        assert user.id is not None
        assert user.email == user_data["email"]

    @pytest.mark.parametrize("field", ["first_name", "last_name", "email", "password"])
    def test_create_user_without_required_fields_raises_error(self, user_built, field):
        user_data = {
            "first_name": user_built.first_name,
            "last_name": user_built.last_name,
            "email": user_built.email,
            "password": user_built.password,
        }
        user_data.pop(field)

        with pytest.raises(TypeError):
            User.objects.create_user(**user_data)

    @pytest.mark.parametrize(
        "optional_field, value",
        [
            ("is_staff", True),
            ("is_active", False),
            ("is_superuser", True),
            ("date_joined", timezone.now()),
        ],
    )
    def test_create_user_with_optional_fields(self, user_built, optional_field, value):
        user_data = {
            "first_name": user_built.first_name,
            "last_name": user_built.last_name,
            "email": user_built.email,
            "password": user_built.password,
            optional_field: value,
        }

        user = User.objects.create_user(**user_data)

        assert user.id is not None
        assert user.email == user_data["email"]
        assert getattr(user, optional_field) == value

    @pytest.mark.parametrize(
        "optional_field, default_value",
        [
            ("is_staff", False),
            ("is_active", True),
            ("is_superuser", False),
        ],
    )
    def test_create_user_without_optional_fields(
        self, user_built, optional_field, default_value
    ):
        user_data = {
            "first_name": user_built.first_name,
            "last_name": user_built.last_name,
            "email": user_built.email,
            "password": user_built.password,
            "is_staff": user_built.is_staff,
            "is_superuser": user_built.is_superuser,
            "is_active": user_built.is_active,
            "date_joined": user_built.date_joined,
        }
        user_data.pop(optional_field)

        user = User.objects.create_user(**user_data)

        assert user.id is not None
        assert user.email == user_data["email"]
        assert getattr(user, optional_field) == default_value

    def test_create_superuser(self, user_built, mocker):
        mock_setup_user_email = mocker.patch(
            "users.models.CustomUserManager.setup_user_email"
        )

        user_data = {
            "first_name": user_built.first_name,
            "last_name": user_built.last_name,
            "email": user_built.email,
            "password": user_built.password,
        }

        user = User.objects.create_superuser(**user_data)

        assert user.id is not None
        assert user.email == user_data["email"]
        assert user.is_staff
        assert user.is_superuser
        mock_setup_user_email.assert_called_once_with(user, verified=True)

    def test_create_superuser_with_is_staff_False_raises_error(self, user_built):
        user_data = {
            "first_name": user_built.first_name,
            "last_name": user_built.last_name,
            "email": user_built.email,
            "password": user_built.password,
            "is_staff": False,
        }

        with pytest.raises(ValueError) as excinfo:
            User.objects.create_superuser(**user_data)

        assert str(excinfo.value) == "Superuser must have is_staff=True."

    def test_create_superuser_with_is_superuser_False_raises_error(self, user_built):
        user_data = {
            "first_name": user_built.first_name,
            "last_name": user_built.last_name,
            "email": user_built.email,
            "password": user_built.password,
            "is_superuser": False,
        }

        with pytest.raises(ValueError) as excinfo:
            User.objects.create_superuser(**user_data)

        assert str(excinfo.value) == "Superuser must have is_superuser=True."

    def test_str_representation(self, user_built):
        user_data = {
            "first_name": user_built.first_name,
            "last_name": user_built.last_name,
            "email": user_built.email,
            "password": user_built.password,
        }
        user = User.objects.create_user(**user_data)

        assert str(user) == user_data["email"]

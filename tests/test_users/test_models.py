import pytest
from django.db.utils import IntegrityError

from apps.users.models import User


pytestmark = [pytest.mark.django_db, pytest.mark.unit]


class TestUserModel:
    def test_create_user(self, user_built):
        user = User.objects.create_user(**user_built)

        assert user.id != None
        assert user.first_name == user_built["first_name"]
        assert user.last_name == user_built["last_name"]
        assert user.email == user_built["email"]
        assert user.check_password(user_built["password"])
        assert not user.is_staff
        assert not user.is_superuser

    def test_create_user_with_existing_email_raises_error(
        self, user_created, user_built
    ):
        new_user = {**user_built, "email": user_created.email}
        with pytest.raises(IntegrityError):
            User.objects.create_user(**new_user)

    def test_create_user_without_any_fields_raises_error(self):
        with pytest.raises(TypeError) as excinfo:
            User.objects.create_user()

        assert (
            str(excinfo.value)
            == "CustomUserManager.create_user() missing 4 required positional arguments: 'email', 'first_name', 'last_name', and 'password'"
        )

    @pytest.mark.parametrize(
        "excluded_field, message_expected",
        [
            ("email", "The given email must be set"),
            ("first_name", "The given first_name must be set"),
            ("last_name", "The given last_name must be set"),
            ("password", "The given password must be set"),
        ],
    )
    def test_create_user_without_required_fields_raises_error(
        self, excluded_field, message_expected, build_user_with
    ):
        params = {"no_%s" % excluded_field: True}
        data = build_user_with(**params)
        with pytest.raises(ValueError) as excinfo:
            User.objects.create_user(**data)
        assert str(excinfo.value) == message_expected

    def test_create_superuser(self, user_built):
        user = User.objects.create_superuser(**user_built)

        assert user.id != None
        assert user.email == user_built["email"]
        assert user.is_staff
        assert user.is_superuser

    def test_create_superuser_with_existing_email_raises_error(
        self, user_created, user_built
    ):
        new_user = {**user_built, "email": user_created.email}
        with pytest.raises(IntegrityError):
            User.objects.create_superuser(**new_user)

    @pytest.mark.parametrize(
        "excluded_field, message_expected",
        [
            ("email", "The given email must be set"),
            ("first_name", "The given first_name must be set"),
            ("last_name", "The given last_name must be set"),
            ("password", "The given password must be set"),
        ],
    )
    def test_create_superuser_without_required_fields_raises_error(
        self, excluded_field, message_expected, build_user_with
    ):
        params = {"no_%s" % excluded_field: True}
        data = build_user_with(**params)
        with pytest.raises(ValueError) as excinfo:
            User.objects.create_superuser(**data)
        assert str(excinfo.value) == message_expected

    def test_create_superuser_with_is_staff_equal_to_False_raises_error(
        self, user_built
    ):
        with pytest.raises(ValueError) as excinfo:
            User.objects.create_superuser(**user_built, is_staff=False)
        assert str(excinfo.value) == "Superuser must have is_staff=True."

    def test_create_superuser_with_is_superuser_equal_to_False_raises_error(
        self, user_built
    ):
        with pytest.raises(ValueError) as excinfo:
            User.objects.create_superuser(**user_built, is_superuser=False)
        assert str(excinfo.value) == "Superuser must have is_superuser=True."

    def test_user_str(self, user_built):
        user = User.objects.create_user(**user_built)
        assert str(user) == user_built["email"]

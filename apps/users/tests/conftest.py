import pytest
from rest_framework.test import APIClient

from users.tests.factories import UserFactory
from users.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_built():
    return UserFactory.build()


@pytest.fixture
def user_created():
    return UserFactory.create()


@pytest.fixture
def create_user_with():
    def create_user(**kwargs):
        return UserFactory.create(**kwargs)

    return create_user


@pytest.fixture
def create_user_with_email_address(create_user_with):
    def create_user(verified=True, **kwargs):
        user_created = create_user_with(**kwargs)
        User.objects.setup_user_email(user_created, verified=verified)
        return {
            "user_created": user_created,
            "user_created_dict": {
                "id": str(user_created.id),
                "email": user_created.email,
                "first_name": user_created.first_name,
                "last_name": user_created.last_name,
            },
        }

    return create_user

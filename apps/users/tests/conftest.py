import pytest
from rest_framework.test import APIClient

from users.tests.factories import UserFactory


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

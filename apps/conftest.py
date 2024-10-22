import pytest
from rest_framework.test import APIClient

from users.tests.factories import UserFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def list_response_keys():
    return {"count", "next", "previous", "results"}


@pytest.fixture
def user_created():
    return UserFactory.create()


@pytest.fixture
def create_batch_users():
    def create_users(size):
        return UserFactory.create_batch(size)

    return create_users

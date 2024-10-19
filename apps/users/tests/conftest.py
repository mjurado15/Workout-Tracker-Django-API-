import pytest

from users.tests.factories import UserFactory


@pytest.fixture
def user_built():
    return UserFactory.build()


@pytest.fixture
def user_created():
    return UserFactory.create()

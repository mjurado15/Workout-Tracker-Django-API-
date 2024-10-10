import pytest

from .factories import UserFactory


def user_to_dict(user_built):
    return {
        "email": user_built.email,
        "first_name": user_built.first_name,
        "last_name": user_built.last_name,
        "password": user_built.password,
    }


@pytest.fixture
def user_built():
    user_built = UserFactory.build()
    return user_to_dict(user_built)


@pytest.fixture
def build_user_with():
    def build_user(**kwargs):
        user_built = UserFactory.build(**kwargs)
        return user_to_dict(user_built)

    return build_user


@pytest.fixture
def user_created():
    return UserFactory.create()


@pytest.fixture
def create_user_with():
    def create_user(**kwargs):
        return UserFactory.create(**kwargs)

    return create_user

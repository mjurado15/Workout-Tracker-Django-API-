import factory
from factory.django import DjangoModelFactory
from django.contrib.auth.hashers import make_password

from apps.users.models import User


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Faker("email")
    password = "test_password"

    @factory.post_generation
    def hash_password(obj, create, extracted, **kwargs):
        if create:
            if extracted:
                obj.password = make_password(extracted)
            else:
                obj.password = make_password(obj.password)
            obj.save()

    # Define a 'trait' to make fields optional
    class Params:
        no_first_name = factory.Trait(first_name=None)
        no_last_name = factory.Trait(last_name=None)
        no_email = factory.Trait(email=None)
        no_password = factory.Trait(password=None)

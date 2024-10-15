import factory
from factory.django import DjangoModelFactory

from apps.workouts.models import ExerciseCategory, Exercise


class ExerciseCategoryFactory(DjangoModelFactory):
    class Meta:
        model = ExerciseCategory

    name = factory.Faker("name")


class ExerciseFactory(DjangoModelFactory):
    class Meta:
        model = Exercise

    name = factory.Faker("name")
    category = factory.SubFactory(ExerciseCategoryFactory)

    class Params:
        create_category = factory.Trait(
            category=factory.LazyFunction(ExerciseCategoryFactory.create)
        )

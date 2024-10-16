import factory
from factory.django import DjangoModelFactory

from tests.test_users.factories import UserFactory

from apps.workouts.models import ExerciseCategory, Exercise, WorkoutPlan


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


class WorkoutPlanFactory(DjangoModelFactory):
    class Meta:
        model = WorkoutPlan

    name = factory.Faker("sentence", nb_words=3)
    description = factory.Faker("sentence", nb_words=10)
    user = factory.SubFactory(UserFactory)

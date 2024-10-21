import factory
from factory.django import DjangoModelFactory

from users.tests.factories import UserFactory
from workouts import models


class ExerciseCategoryFactory(DjangoModelFactory):
    class Meta:
        model = models.ExerciseCategory

    name = factory.Faker("sentence", nb_words=3)


class ExerciseFactory(DjangoModelFactory):
    class Meta:
        model = models.Exercise

    name = factory.Faker("sentence", nb_words=3)
    description = factory.Faker("sentence", nb_words=10)
    category = factory.SubFactory(ExerciseCategoryFactory)


class WorkoutFactory(DjangoModelFactory):
    class Meta:
        model = models.Workout

    name = factory.Faker("sentence", nb_words=3)
    description = factory.Faker("sentence", nb_words=10)
    user = factory.SubFactory("users.tests.factories.UserFactory")

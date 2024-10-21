import factory
from factory.django import DjangoModelFactory

from workouts import models


class ExerciseCategoryFactory(DjangoModelFactory):
    class Meta:
        model = models.ExerciseCategory

    name = factory.Faker("sentence", nb_words=3)

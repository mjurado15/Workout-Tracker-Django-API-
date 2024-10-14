import factory
from factory.django import DjangoModelFactory

from apps.workouts.models import ExerciseCategory, Exercise


class ExerciseCategoryFactory(DjangoModelFactory):
    class Meta:
        model = ExerciseCategory

    name = "strength"


class ExerciseFactory(DjangoModelFactory):
    class Meta:
        model = Exercise

    name = "Bicep curl"
    category = factory.SubFactory(ExerciseCategoryFactory)

    class Params:
        create_category = factory.Trait(
            category=factory.LazyFunction(ExerciseCategoryFactory.create)
        )

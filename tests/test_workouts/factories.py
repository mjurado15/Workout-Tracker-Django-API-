import factory
from factory.django import DjangoModelFactory

from tests.test_users.factories import UserFactory

from apps.workouts.models import (
    ExerciseCategory,
    Exercise,
    WorkoutPlan,
    ExercisePlan,
    WorkoutComment,
)


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


class ExercisePlanFactory(DjangoModelFactory):
    class Meta:
        model = ExercisePlan

    name = factory.Faker("sentence", nb_words=5)
    description = factory.Faker("sentence", nb_words=10)
    sets = factory.Faker("pyint", min_value=1, max_value=5)
    reps = factory.Faker("pyint", min_value=1, max_value=30)
    weight = factory.Faker("pyint", min_value=10, max_value=100)
    weight_measure_unit = "pound"

    workout_plan = factory.SubFactory(WorkoutPlanFactory)
    exercise = factory.SubFactory(ExerciseFactory)


class CommentFactory(DjangoModelFactory):
    class Meta:
        model = WorkoutComment

    comment = factory.Faker("sentence", nb_words=10)
    workout_plan = factory.SubFactory(WorkoutPlanFactory)

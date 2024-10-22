import random

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


class ExercisePlanFactory(DjangoModelFactory):
    class Meta:
        model = models.ExercisePlan

    name = factory.Faker("sentence", nb_words=3)
    description = factory.Faker("sentence", nb_words=10)
    sets = factory.Faker("pyint", min_value=0, max_value=10)
    reps = factory.Faker("pyint", min_value=10, max_value=30)
    exercise = factory.SubFactory(ExerciseFactory)
    workout = factory.SubFactory(WorkoutFactory)


class WorkoutCommentFactory(DjangoModelFactory):
    class Meta:
        model = models.WorkoutComment

    comment = factory.Faker("sentence", nb_words=10)
    workout = factory.SubFactory(WorkoutFactory)


class ScheduledDateFactory(DjangoModelFactory):
    class Meta:
        model = models.ScheduledWorkoutDate

    date = factory.Faker("date_this_month", before_today=False, after_today=True)
    time = factory.Faker("time_object")
    workout = factory.SubFactory(WorkoutFactory)


class RecurringAlertFactory(DjangoModelFactory):
    class Meta:
        model = models.RecurringWorkoutAlert

    time = factory.Faker("time_object")
    week_days = random.sample(range(7), random.randint(0, 7))
    workout = factory.SubFactory(WorkoutFactory)

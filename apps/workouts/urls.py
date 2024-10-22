from rest_framework.routers import SimpleRouter
from django.urls import path, include

from workouts.views import workout_views, exercise_category_views

router = SimpleRouter()

router.register(
    "exercise_categories",
    exercise_category_views.ExerciseCategoryViews,
    basename="exercise-categories",
)
router.register("workouts", workout_views.WorkoutViews, basename="workouts")


urlpatterns = [
    path("", include(router.urls)),
]

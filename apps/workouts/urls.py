from rest_framework.routers import SimpleRouter
from django.urls import path, include

from . import views

router = SimpleRouter()

router.register(
    "exercise_categories", views.ExerciseCategoryViews, basename="exercise-categories"
)
router.register("workouts", views.WorkoutViews, basename="workouts")

urlpatterns = [
    path("", include(router.urls)),
]

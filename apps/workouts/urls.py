from django.urls import path, include
from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter()

router.register(
    "exercise-categories", views.ExerciseCategoryViewSet, basename="exercise-categories"
)
router.register("exercises", views.ExerciseViewSet, basename="exercises")
router.register("workout-plans", views.WorkoutPlanViewSet, basename="workout-plans")

urlpatterns = [
    path("", include(router.urls)),
]

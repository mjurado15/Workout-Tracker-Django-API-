from rest_framework.routers import SimpleRouter
from django.urls import path, include

from . import views

router = SimpleRouter()

router.register(
    "exercise-categories", views.ExerciseCategoryViews, basename="exercise-categories"
)

urlpatterns = [
    path("", include(router.urls)),
]

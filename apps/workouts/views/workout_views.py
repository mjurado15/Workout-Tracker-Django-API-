from rest_framework import viewsets

from workouts import models, serializers
from workouts.views import comment_views
from workouts.views import exercise_plan_views


class WorkoutViews(
    viewsets.ModelViewSet,
    exercise_plan_views.ExercisePlanViews,
    comment_views.CommentViews,
):
    serializer_class = serializers.WorkoutSerializer

    def get_queryset(self):
        authenticated_user = self.request.user
        return models.Workout.objects.filter(user=authenticated_user).order_by(
            "-created_at"
        )

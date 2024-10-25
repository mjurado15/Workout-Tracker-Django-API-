from rest_framework import viewsets

from workouts import models, serializers


class WorkoutViews(viewsets.ModelViewSet):
    serializer_class = serializers.WorkoutSerializer

    def get_queryset(self):
        authenticated_user = self.request.user
        return models.Workout.objects.filter(user=authenticated_user).order_by(
            "-created_at"
        )

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from workouts.models import RecurringWorkoutAlert
from workouts.serializers import RecurringAlertSerializer


class RecurringAlertViews:
    @action(methods=["GET", "POST"], detail=True)
    def recurring_alerts(self, request, *args, **kwargs):
        workout = self.get_object()
        recurring_alert_serializer = RecurringAlertSerializer

        if request.method == "GET":
            if not workout.is_recurrent():
                return Response(
                    {"detail": "The workout is not recurrent."},
                    status=status.HTTP_412_PRECONDITION_FAILED,
                )

            recurring_alerts = workout.recurring_alerts.all().order_by("time")
            queryset = self.filter_queryset(recurring_alerts)

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = recurring_alert_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = recurring_alert_serializer(queryset, many=True)
            return Response(serializer.data)

        if request.method == "POST":
            if not workout.is_recurrent():
                workout.switch_to_recurrent()

            serializer = recurring_alert_serializer(
                data=request.data, context={"workout": workout}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        methods=["GET", "PATCH", "DELETE"],
        detail=True,
        url_path="recurring_alerts/(?P<recurring_alert_pk>[^/.]+)",
    )
    def recurring_alert_details(self, request, *args, **kwargs):
        workout = self.get_object()
        recurring_alert = get_object_or_404(
            RecurringWorkoutAlert,
            pk=kwargs.get("recurring_alert_pk"),
            workout=workout,
        )
        recurring_alert_serializer = RecurringAlertSerializer

        if request.method == "GET":
            data = recurring_alert_serializer(recurring_alert).data
            return Response(data)

        if request.method == "PATCH":
            serializer = recurring_alert_serializer(
                recurring_alert, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        if request.method == "DELETE":
            recurring_alert.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

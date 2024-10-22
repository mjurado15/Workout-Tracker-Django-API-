from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from workouts.models import ScheduledWorkoutDate
from workouts.serializers import ScheduledDateSerializer


class ScheduledDateViews:
    @action(methods=["GET", "POST"], detail=True)
    def scheduled_dates(self, request, *args, **kwargs):
        workout = self.get_object()
        scheduled_date_serializer = ScheduledDateSerializer

        if request.method == "GET":
            if not workout.is_scheduled():
                return Response(
                    {"detail": "The workout is not scheduled."},
                    status=status.HTTP_412_PRECONDITION_FAILED,
                )

            scheduled_dates = workout.scheduled_dates.all().order_by("date", "time")
            queryset = self.filter_queryset(scheduled_dates)

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = scheduled_date_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = scheduled_date_serializer(queryset, many=True)
            return Response(serializer.data)

        if request.method == "POST":
            if not workout.is_scheduled():
                workout.switch_to_scheduled()

            serializer = scheduled_date_serializer(
                data=request.data, context={"workout": workout}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        methods=["GET", "PATCH", "DELETE"],
        detail=True,
        url_path="scheduled_dates/(?P<scheduled_date_pk>[^/.]+)",
    )
    def scheduled_date_details(self, request, *args, **kwargs):
        workout = self.get_object()
        scheduled_date = get_object_or_404(
            ScheduledWorkoutDate,
            pk=kwargs.get("scheduled_date_pk"),
            workout=workout,
        )
        scheduled_date_serializer = ScheduledDateSerializer

        if request.method == "GET":
            data = scheduled_date_serializer(scheduled_date).data
            return Response(data)

        if request.method == "PATCH":
            serializer = scheduled_date_serializer(
                scheduled_date, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        if request.method == "DELETE":
            scheduled_date.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

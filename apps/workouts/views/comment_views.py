from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from workouts.models import WorkoutComment
from workouts.serializers import CommentSerializer


class CommentViews:
    @action(methods=["GET", "POST"], detail=True)
    def comments(self, request, *args, **kwargs):
        workout = self.get_object()
        comment_serializer = CommentSerializer

        if request.method == "GET":
            comments = workout.comments.all().order_by("-created_at")
            queryset = self.filter_queryset(comments)

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = comment_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = comment_serializer(queryset, many=True)
            return Response(serializer.data)

        if request.method == "POST":
            serializer = comment_serializer(
                data=request.data, context={"workout": workout}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        methods=["GET", "PATCH", "DELETE"],
        detail=True,
        url_path="comments/(?P<comment_pk>[^/.]+)",
    )
    def comment_detail(self, request, *args, **kwargs):
        workout = self.get_object()
        comment = get_object_or_404(
            WorkoutComment, pk=kwargs.get("comment_pk"), workout=workout
        )
        comment_serializer = CommentSerializer

        if request.method == "GET":
            data = comment_serializer(comment).data
            return Response(data)

        if request.method == "PATCH":
            serializer = comment_serializer(comment, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        if request.method == "DELETE":
            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

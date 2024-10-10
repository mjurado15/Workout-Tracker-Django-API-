from rest_framework import viewsets, views, status
from rest_framework.response import Response

from . import serializers


class SignupView(views.APIView):
    def post(self, request, *args, **kwargs):
        serializer = serializers.SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from drf_spectacular.utils import extend_schema

from . import serializers


class SignupView(APIView):
    permission_classes = ()
    authentication_classes = ()

    @extend_schema(
        request=serializers.SignupSerializer,
        responses=serializers.SignupSerializer,
    )
    def post(self, request, *args, **kwargs):
        serializer = serializers.SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CustomTokenObtainPairView(TokenObtainPairView):
    @extend_schema(responses=serializers.LoginResponseSerializer)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

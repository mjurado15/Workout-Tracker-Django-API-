from rest_framework import serializers
from rest_framework_simplejwt import serializers as simplejwt_serializers

from . import models


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ("id", "email", "first_name", "last_name")


class SignupSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ("password",)
        extra_kwargs = {
            "password": {"min_length": 8, "write_only": True},
        }

    def create(self, validated_data):
        return models.User.objects.create_user(**validated_data)


class TokenObtainPairSerializer(simplejwt_serializers.TokenObtainPairSerializer):
    def validate(self, attrs):
        tokens = super().validate(attrs)
        data = {"user": UserSerializer(self.user).data, **tokens}
        return data


class LoginResponseSerializer(serializers.Serializer):
    access = serializers.CharField(max_length=55)
    refresh = serializers.CharField(max_length=55)
    user = UserSerializer()

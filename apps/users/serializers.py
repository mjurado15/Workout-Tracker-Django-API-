from rest_framework import serializers
from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth.forms import PasswordResetForm

from dj_rest_auth import serializers as auth_serializers
from dj_rest_auth.registration import serializers as auth_regist_serializers
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email

from . import models
from .forms import AllAuthPasswordResetForm


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ("id", "email", "first_name", "last_name")


class RegisterSerializer(auth_regist_serializers.RegisterSerializer):
    username = None
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)

    def get_cleaned_data(self):
        return {
            "email": self.validated_data.get("email", ""),
            "first_name": self.validated_data.get("first_name", ""),
            "last_name": self.validated_data.get("last_name", ""),
            "password1": self.validated_data.get("password1", ""),
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        user = adapter.save_user(request, user, self, commit=False)

        if "password1" in self.cleaned_data:
            try:
                adapter.clean_password(self.cleaned_data["password1"], user=user)
            except DjangoValidationError as exc:
                raise serializers.ValidationError(
                    detail=serializers.as_serializer_error(exc)
                )
        user.save()
        self.custom_signup(request, user)
        setup_user_email(request, user, [])
        return user


class LoginSerializer(auth_serializers.LoginSerializer):
    username = None
    email = serializers.EmailField()


class VerifyEmailSerializer(auth_regist_serializers.VerifyEmailSerializer):
    def validate_key(self, value):
        from urllib.parse import unquote

        return unquote(value)


class PasswordResetSerializer(auth_serializers.PasswordResetSerializer):
    @property
    def password_reset_form_class(self):
        if "allauth" in settings.INSTALLED_APPS:
            return AllAuthPasswordResetForm
        else:
            return PasswordResetForm

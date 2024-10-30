from django.conf import settings

from dj_rest_auth.registration import views as registration_views
from dj_rest_auth.serializers import JWTSerializer
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client

from drf_spectacular.utils import extend_schema

from . import serializers


class VerifyEmailView(registration_views.VerifyEmailView):
    def get_serializer(self, *args, **kwargs):
        return serializers.VerifyEmailSerializer(*args, **kwargs)


class GoogleLogin(registration_views.SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = settings.CLIENT_URL
    client_class = OAuth2Client

    @extend_schema(responses={200: JWTSerializer})
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

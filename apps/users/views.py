from drf_spectacular.utils import extend_schema
from dj_rest_auth.registration import views as registration_views

from . import serializers


class VerifyEmailView(registration_views.VerifyEmailView):
    def get_serializer(self, *args, **kwargs):
        return serializers.VerifyEmailSerializer(*args, **kwargs)

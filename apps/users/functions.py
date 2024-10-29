from urllib.parse import quote

from django.http import HttpRequest
from django.urls import reverse

from allauth.core.internal.httpkit import get_frontend_url
from allauth.utils import build_absolute_uri


def get_reset_password_from_params_url(request: HttpRequest, **kwargs) -> str:
    """
    Method intented to be overriden in case the password reset email
    needs to point to your frontend/SPA.
    """
    url = get_frontend_url(request, "account_reset_password_from_key", **kwargs)
    if not url:
        path = reverse(
            "account_reset_password_from_key", kwargs={"uidb36": "UID", "key": "KEY"}
        )
        path = path.replace("UID-KEY", quote(kwargs.get("key", "")))
        url = build_absolute_uri(request, path)
    return url

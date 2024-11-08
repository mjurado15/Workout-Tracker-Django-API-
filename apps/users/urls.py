from django.urls import path

from dj_rest_auth.registration import views as registration_views
from dj_rest_auth import views as auth_views
from dj_rest_auth.app_settings import api_settings

from . import views as local_views


urlpatterns = [
    path("signup/", registration_views.RegisterView.as_view(), name="signup"),
    path(
        "verify-email/",
        local_views.VerifyEmailView.as_view(),
        name="rest_verify_email",
    ),
    path(
        "resend-email/",
        registration_views.ResendEmailVerificationView.as_view(),
        name="rest_resend_email",
    ),
    # URLs that do not require a session or valid token
    path(
        "password/reset/",
        auth_views.PasswordResetView.as_view(),
        name="rest_password_reset",
    ),
    path(
        "password/reset/confirm/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="rest_password_reset_confirm",
    ),
    path("login/", local_views.LoginView.as_view(), name="rest_login"),
    # URLs that require a user to be logged in with a valid session / token.
    path("logout/", auth_views.LogoutView.as_view(), name="rest_logout"),
    path("user/", auth_views.UserDetailsView.as_view(), name="rest_user_details"),
    path(
        "password/change/",
        auth_views.PasswordChangeView.as_view(),
        name="rest_password_change",
    ),
    # Social authentication
    path("google/", local_views.GoogleLogin.as_view(), name="google_login"),
]


if api_settings.USE_JWT:
    from rest_framework_simplejwt.views import TokenVerifyView

    from dj_rest_auth.jwt_auth import get_refresh_view

    urlpatterns += [
        path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
        path("token/refresh/", get_refresh_view().as_view(), name="token_refresh"),
    ]

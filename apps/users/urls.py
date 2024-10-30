from django.urls import path, include

from dj_rest_auth.registration import views as registration_views

from . import views


urlpatterns = [
    path("signup/", registration_views.RegisterView.as_view(), name="signup"),
    path(
        "verify-email/",
        views.VerifyEmailView.as_view(),
        name="rest_verify_email",
    ),
    path(
        "resend-email/",
        registration_views.ResendEmailVerificationView.as_view(),
        name="rest_resend_email",
    ),
    path("", include("dj_rest_auth.urls")),
    path("google/", views.GoogleLogin.as_view(), name="google_login"),
]

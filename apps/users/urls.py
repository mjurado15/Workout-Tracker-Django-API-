from django.urls import path
from rest_framework_simplejwt import views as simplejwt_views

from . import views


urlpatterns = [
    path("signup/", views.SignupView.as_view(), name="signup"),
    path("login/", simplejwt_views.TokenObtainPairView.as_view(), name="login"),
    path(
        "refresh_token/",
        simplejwt_views.TokenRefreshView.as_view(),
        name="refresh-token",
    ),
]

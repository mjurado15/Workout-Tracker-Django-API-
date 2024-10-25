from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    path("signup/", views.SignupView.as_view(), name="signup"),
    path("login/", views.CustomTokenObtainPairView.as_view(), name="login"),
    path("refresh_token/", TokenRefreshView.as_view(), name="refresh-token"),
]

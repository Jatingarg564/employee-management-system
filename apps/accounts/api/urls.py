from django.urls import path

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from apps.accounts.api.views import (
    AccountActivationAPIView,
    LoginAPIView,
    ValidateActivationTokenAPIView,
)


urlpatterns = [
    path(
        "login/",
        LoginAPIView.as_view(),
        name="login",
    ),

    path(
        "validate-token/",
        ValidateActivationTokenAPIView.as_view(),
        name="validate-activation-token",
    ),

    path(
        "activate/",
        AccountActivationAPIView.as_view(),
        name="activate-account",
    ),

    path(
        "token/refresh/",
        TokenRefreshView.as_view(),
        name="token-refresh",
    ),
]
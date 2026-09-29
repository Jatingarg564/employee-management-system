from django.urls import path

from apps.accounts.api.views import (
    AccountActivationAPIView,
    LoginAPIView,
    LogoutAPIView,
    TokenRefreshAPIView,
    ValidateActivationTokenAPIView,
)

urlpatterns = [
    path("login/", LoginAPIView.as_view(), name="login"),
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
        TokenRefreshAPIView.as_view(),
        name="token-refresh",
    ),
    path(
        "logout/",
        LogoutAPIView.as_view(),
        name="logout",
    ),
]
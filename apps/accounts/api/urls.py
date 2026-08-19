from django.urls import path

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from apps.accounts.api.views import (
    LoginAPIView,
)


urlpatterns = [
    path(
        "login/",
        LoginAPIView.as_view(),
        name="login",
    ),

    path(
        "token/refresh/",
        TokenRefreshView.as_view(),
        name="token-refresh",
    ),
]
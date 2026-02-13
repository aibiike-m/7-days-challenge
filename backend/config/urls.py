from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.users.views import (
    UserViewSet,
    LogoutView,
    login_by_email,
)
from apps.users.social_views import exchange_token
from apps.users.views import cancel_email_change
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    path("admin/", admin.site.urls),
    # Authentication
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/", include("djoser.urls")),
    path("api/auth/", include("djoser.urls.jwt")),
    path("api/auth/google/", exchange_token, name="google_login"),
    path("api/logout/", LogoutView.as_view(), name="logout"),
    path("api/auth/login-by-email/", login_by_email, name="login_by_email"),
    path(
        "api/users/cancel-email-change/",
        cancel_email_change,
        name="cancel_email_change",
    ),
    # API
    path("api/", include("apps.challenges.urls")),
    path("api/", include(router.urls)),
]

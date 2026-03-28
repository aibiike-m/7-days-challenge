from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from config.settings.base import env
from apps.users.views import (
    UserViewSet,
    LogoutView,
    login_by_email,
    cancel_email_change,
    confirm_delete_account,
    request_password_reset,
    verify_password_reset_code,
    confirm_password_reset,
)
from apps.users.social_views import exchange_token

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
admin_url = env("ADMIN_URL").strip("/") + "/"

def health_check(request):
    return JsonResponse({"status": "ok"})

urlpatterns = [
    path("health/", health_check),
    path(admin_url, admin.site.urls),
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
    path(
        "api/users/confirm-account-deletion/",
        confirm_delete_account,
        name="confirm_delete_account",
    ),
    path(
        "api/auth/request-password-reset/",
        request_password_reset,
        name="request_password_reset",
    ),
    path(
        "api/auth/verify-password-reset-code/",
        verify_password_reset_code,
        name="verify_password_reset_code",
    ),
    path(
        "api/auth/confirm-password-reset/",
        confirm_password_reset,
        name="confirm_password_reset",
    ),
    # API
    path("api/", include("apps.challenges.urls")),
    path("api/", include(router.urls)),
    # Swagger
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]

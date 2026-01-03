from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.users.views import (
    UserViewSet,
    RegisterView,
    LogoutView,
    google_login,
    login_by_email,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    path("admin/", admin.site.urls),
    # Authentication
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/register/", RegisterView.as_view()),
    path("api/logout/", LogoutView.as_view()),
    path("api/auth/google/", google_login, name="google_login"),
    path("api/auth/login-by-email/", login_by_email, name="login_by_email"),
    # API
    path("api/", include("apps.challenges.urls")),
    path("api/", include(router.urls)),
]
from django.contrib import admin
from django.urls import path, include
from apps.users.views import RegisterView, LogoutView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/", include("apps.challenges.urls")),
    path("api/register/", RegisterView.as_view()),
    path("api/logout/", LogoutView.as_view()),
]

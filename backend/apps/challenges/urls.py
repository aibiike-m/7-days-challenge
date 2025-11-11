from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChallengeViewSet, TaskViewSet

router = DefaultRouter()
router.register(r"challenges", ChallengeViewSet, basename="challenge")
router.register(r"tasks", TaskViewSet, basename="task")

urlpatterns = [
    path("", include(router.urls)),
]

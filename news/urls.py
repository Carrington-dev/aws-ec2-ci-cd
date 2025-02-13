from django.urls import path, include
from rest_framework.routers import DefaultRouter

from news.views import PostViewSet

router = DefaultRouter()
router.register("posts", PostViewSet, basename="post")

urlpatterns = [
    path("api/v1/", include(router.urls))
]

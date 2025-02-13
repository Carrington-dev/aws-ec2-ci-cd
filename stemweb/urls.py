from django.contrib import admin
from django.urls import path, include

from stemweb.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", view=home, name="home"),
    path("api/v1/", include("news.urls")),
]

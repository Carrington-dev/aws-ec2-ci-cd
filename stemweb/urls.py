from django.contrib import admin
from django.urls import path

from stemweb.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", view=home, name="home")
]

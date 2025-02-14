from django.contrib import admin
from django.urls import path, include

from stemweb.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", view=home, name="home"),
    path("api/v1/", include("news.urls")),
    path('api/v1/auth/', include('djoser.urls')),
    path("api/v1/auth/", include("djoser.urls.jwt")),
]


admin.site.site_title = "Vroomhive Services"
admin.site.site_header = "Vroomhive Inc"
admin.site.index_title = "Vroomhive welcomes you!!!"
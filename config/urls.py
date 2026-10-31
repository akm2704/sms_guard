from django.contrib import admin
from django.urls import path

from apps.analysis.views import health
from config.views import home

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("api/v1/health/", health, name="api-health"),
]

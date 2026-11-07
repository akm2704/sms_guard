"""URL routes for SMS Guard's training-stage demonstration prototype."""
from django.contrib import admin
from django.urls import path

from apps.analysis.views import health, sms_check
from config.views import home

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("check/sms/", sms_check, name="sms-check"),
    path("api/v1/health/", health, name="api-health"),
]

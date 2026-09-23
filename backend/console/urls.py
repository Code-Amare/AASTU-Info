from django.urls import path
from .views import PlatformSettingsView

urlpatterns = [
    path("settings/", PlatformSettingsView.as_view()),
]

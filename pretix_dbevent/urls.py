from django.urls import path

from .views import DBEventSettingsView

urlpatterns = [
    path(
        "control/event/<str:organizer>/<str:event>/dbevent/settings",
        DBEventSettingsView.as_view(),
        name="settings",
    ),
]

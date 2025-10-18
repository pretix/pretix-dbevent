from django.urls import reverse
from pretix.base.models import Event
from pretix.control.views.event import EventSettingsFormView, EventSettingsViewMixin

from .forms import DBEventSettingsForm


class DBEventSettingsView(EventSettingsViewMixin, EventSettingsFormView):
    model = Event
    form_class = DBEventSettingsForm
    template_name = "pretix_dbevent/settings.html"
    permission = "can_change_event_settings"

    def get_success_url(self) -> str:
        return reverse(
            "plugins:pretix_dbevent:settings",
            kwargs={
                "organizer": self.request.event.organizer.slug,
                "event": self.request.event.slug,
            },
        )

    def form_success(self):
        if not self.request.event.settings.dbevent_override_texts:
            del self.request.event.settings.dbevent_advertising_title
            del self.request.event.settings.dbevent_advertising_content

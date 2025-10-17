from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _, pgettext_lazy
from pretix.base.forms import SettingsForm
from urllib.parse import parse_qs, urlparse

from .models import ItemDBEventConfig


class ItemDBEventConfigForm(forms.ModelForm):
    issue_coupons = forms.BooleanField(
        label=pgettext_lazy(
            "dbevent", "Display DB Event Offer if this product is purchased"
        ),
        required=False,
    )

    class Meta:
        model = ItemDBEventConfig
        fields = ["issue_coupons"]
        exclude = []

    def __init__(self, *args, **kwargs):
        event = kwargs.pop("event")  # NoQA
        instance = kwargs.get("instance")  # NoQA
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        if not self.cleaned_data["issue_coupons"]:
            if self.instance.pk:
                self.instance.delete()
            else:
                return
        else:
            v = self.cleaned_data["issue_coupons"]
            self.instance.issue_coupons = v
            return super().save(commit=commit)


class DBEventSettingsForm(SettingsForm):
    dbevent_event_id = forms.CharField(
        label=_("DB Event ID"),
        help_text=_(
            "The ID of your event as displayed in the DB Event Offers portal. If your URL is "
            "<code>https://www.veranstaltungsticket-bahn.de/?event=33148&language=de</code>, or "
            "<code>https://www.eventanreise-bahn.de/de/events/33148</code>, please enter "
            "<code>33148</code>."
        ),
        required=False,
    )

    def clean_dbevent_event_id(self):
        if self.cleaned_data.get("dbevent_event_id", "").isnumeric():
            return self.cleaned_data.get("dbevent_event_id")
        elif self.cleaned_data.get("dbevent_event_id", None) == "":
            return None
        else:
            try:
                return parse_qs(
                    urlparse(self.cleaned_data.get("dbevent_event_id")).query
                )["event"][0]
            except KeyError:
                raise ValidationError(_("Invalid DB Event ID"))

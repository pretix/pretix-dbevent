from django.db import models
from django.utils.translation import gettext_lazy as _


class ItemDBEventConfig(models.Model):
    item = models.OneToOneField(
        "pretixbase.Item",
        related_name="dbevent_item",
        on_delete=models.CASCADE,
    )
    issue_coupons = models.BooleanField(
        verbose_name=_("Display DB Event Offer if this product is purchased"),
        default=False,
    )

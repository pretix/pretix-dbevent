import copy
from django.dispatch import receiver
from django.template.loader import get_template
from django.urls import resolve, reverse
from django.utils.translation import gettext_lazy as _, gettext_noop
from i18nfield.strings import LazyI18nString

from pretix.base.models import Event, Order
from pretix.base.settings import settings_hierarkey
from pretix.base.signals import event_copy_data, item_copy_data
from pretix.control.signals import item_forms, nav_event_settings
from pretix.presale.signals import html_head, order_info, position_info

from .forms import ItemDBEventConfigForm
from .helpers import dbevent_url_context
from .models import ItemDBEventConfig


@receiver(nav_event_settings, dispatch_uid="dbevent_nav")
def nav_event_settings(sender, request, **kwargs):
    url = resolve(request.path_info)
    if not request.user.has_event_permission(
        request.organizer, request.event, "can_view_orders", request=request
    ):
        return []
    return [
        {
            "label": _("DB Event Offer"),
            "icon": "train",
            "url": reverse(
                "plugins:pretix_dbevent:settings",
                kwargs={
                    "event": request.event.slug,
                    "organizer": request.organizer.slug,
                },
            ),
            "active": url.namespace == "plugins:pretix_dbevent",
        }
    ]


@receiver(item_forms, dispatch_uid="dbevent_item_forms")
def control_item_forms(sender, request, item, **kwargs):
    try:
        inst = ItemDBEventConfig.objects.get(item=item)
    except ItemDBEventConfig.DoesNotExist:
        inst = ItemDBEventConfig(item=item)
    return ItemDBEventConfigForm(
        instance=inst,
        event=sender,
        data=(request.POST if request.method == "POST" else None),
        prefix="dbeventitem",
    )


@receiver(item_copy_data, dispatch_uid="dbevent_item_copy")
def copy_item(sender, source, target, **kwargs):
    try:
        inst = ItemDBEventConfig.objects.get(item=source)
        inst = copy.copy(inst)
        inst.pk = None
        inst.item = target
        inst.save()
    except ItemDBEventConfig.DoesNotExist:
        pass


@receiver(signal=event_copy_data, dispatch_uid="dbevent_copy_data")
def event_copy_data_receiver(sender, other, question_map, item_map, **kwargs):
    for ip in ItemDBEventConfig.objects.filter(item__event=other):
        ip = copy.copy(ip)
        ip.pk = None
        ip.event = sender
        ip.item = item_map[ip.item_id]
        ip.save()


@receiver(order_info, dispatch_uid="dbevent_order_info")
def order_info(sender: Event, order: Order, request, **kwargs):
    if not ItemDBEventConfig.objects.filter(
        item__in=order.positions.all().values_list("item"), issue_coupons=True
    ).exists():
        return ""

    template = get_template("pretix_dbevent/order_position_info.html")
    return template.render({
        "dbevent_advertising_text": str(sender.settings.dbevent_advertising_content).format_map(dbevent_url_context(request)),
    }, request)


@receiver(position_info, dispatch_uid="dbevent_position_info")
def position_info(sender: Event, order: Order, position, request, **kwargs):
    if (
        not hasattr(position.item, "dbevent_item")
        or not position.item.dbevent_item.issue_coupons
    ):
        return ""

    template = get_template("pretix_dbevent/order_position_info.html")
    return template.render({
        "dbevent_advertising_text": str(sender.settings.dbevent_advertising_content).format_map(dbevent_url_context(request)),
    }, request)


@receiver(html_head, dispatch_uid="dbevent_html_head")
def html_head_presale(sender, request=None, **kwargs):
    template = get_template("pretix_dbevent/presale_head.html")
    return template.render({})


settings_hierarkey.add_default("dbevent_event_id", None, int)
settings_hierarkey.add_default("dbevent_override_texts", False, bool)
settings_hierarkey.add_default("dbevent_advertising_title", LazyI18nString.from_gettext(gettext_noop(
    "Always a good move: Travel by train to your event"
)), LazyI18nString)
settings_hierarkey.add_default("dbevent_advertising_content", LazyI18nString.from_gettext(gettext_noop(
    "For *{event}* participants exclusively: Travel comfortable, sustainable and affordable throughout "
    "Germany by train.\n"
    "\n"
    "DB event offers provide you with several benefits:\n"
    "\n"
    "- Attractive prices: low entry price from just EUR 16.19\n"
    "- Flexible combination: apply additional BahnCard discount\n"
    "- Sustainability guaranteed: arrival and departure on Deutsche Bahn trains using 100% renewable power\n"
    "- Use your time effectively: work or relax on your journey\n"
    "\n"
    "[Book online now]({booking_url}), discover all DB event offers for your preferred route and secure your "
    "discounted ticket. [Terms and Conditions apply]({faq_url})"
)), LazyI18nString)

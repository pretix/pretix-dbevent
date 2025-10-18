from django.http import HttpRequest


def dbevent_url_context(request: HttpRequest):
    dbevent_event_id = request.event.settings.dbevent_event_id
    locale = "de" if request.LANGUAGE_CODE.startswith("de") else "en"

    return {
        "booking_url": f"https://www.eventanreise-bahn.de/{locale}/events/{dbevent_event_id}",
        "event_id": dbevent_event_id,
        "faq_url": "https://www.bahn.de/eventangebote-teilnehmende",
        "event": str(request.event),
    }

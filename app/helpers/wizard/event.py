import json

from app.helpers.data_getter import DataGetter
from app.helpers.helpers import represents_int


def get_event_json(event_id):

    if represents_int(event_id):
        event = DataGetter.get_event(event_id)
    else:
        event = event_id

    result = {
        "id": event.id,
        "name": event.name,
        "location_name": event.location_name,
        "show_map": event.show_map,
        "start_time_date": event.start_time.strftime('%m/%d/%Y') if event.start_time else '',
        "start_time_time": event.start_time.strftime('%H:%M') if event.start_time else '',
        "end_time_date": event.end_time.strftime('%m/%d/%Y') if event.end_time else '',
        "end_time_time": event.end_time.strftime('%H:%M') if event.end_time else '',
        "timezone": event.timezone,
        "description": event.description,
        "background_url": event.background_url,
        "logo": event.logo,
        "has_organizer_info": (event.organizer_description != '' or event.organizer_name != ''),
        "organizer_name": event.organizer_name,
        "organizer_description": event.organizer_description,
        "event_url": event.event_url,
        "social_links": [],
        "ticket_include": event.ticket_include,
        "tickets": [],
        "ticket_url": event.ticket_url,
        "discount_code_id": event.discount_code_id,
        "discount_code": '',
        "payment_country": event.payment_country,
        "payment_currency": event.payment_currency,
        "pay_by_paypal": event.pay_by_paypal,
        "pay_by_stripe": event.pay_by_stripe,
        "pay_by_cheque": event.pay_by_cheque,
        "pay_by_bank": event.pay_by_bank,
        "pay_onsite": event.pay_onsite,
        "privacy": event.privacy,
        "type": event.type,
        "topic": event.topic,
        "sub_topic": event.sub_topic,
        "has_code_of_conduct": event.code_of_conduct != '',
        "code_of_conduct": event.code_of_conduct,
        "copyright": event.copyright.serialize if event.copyright else None,
        "tax_allow": event.tax_allow,
        "tax": event.tax.serialize if event.tax else None,
        "latitude": event.latitude,
        "longitude": event.longitude,
        "stripe": event.stripe.serialize if event.stripe else None,
        "state": event.state
    }

    for social_link in event.social_link:
        if social_link.name == 'External Event URL':
            result["event_url"] = social_link.link
        else:
            result["social_links"].append(social_link.serialize)

    for ticket in event.tickets:
        result["tickets"].append(ticket.serialize)

    if event.stripe:
        result['stripe']['linked'] = True

    return result


def save_event_from_json(json):
    pass

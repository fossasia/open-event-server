import os
from datetime import datetime

from PIL import Image
from flask import url_for, abort
from flask.ext import login

from app.helpers.data import save_to_db, record_activity
from app.helpers.data_getter import DataGetter
from app.helpers.helpers import represents_int
from app.helpers.static import EVENT_LICENCES
from app.helpers.storage import UPLOAD_PATHS
from app.helpers.wizard.helpers import save_resized_image, save_event_image, get_path_of_temp_url, \
    get_searchable_location_name, get_event_time_field_format
from app.models import db
from app.models.email_notifications import EmailNotification
from app.models.event import Event
from app.models.event_copyright import EventCopyright
from app.models.image_sizes import ImageSizes
from app.models.role import Role
from app.models.stripe_authorization import StripeAuthorization
from app.models.tax import Tax
from app.models.ticket import Ticket, ticket_tags_table, TicketTag
from app.models.user import ORGANIZER
from app.models.users_events_roles import UsersEventsRoles
from app.models.social_link import SocialLink


def get_event_json(event_id):
    """
    Generate a json to seed the wizard with from an exisiting event
    :param event_id:
    :return:
    """
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
        "paypal_email": event.paypal_email,
        "pay_by_cheque": event.pay_by_cheque,
        "pay_by_bank": event.pay_by_bank,
        "pay_onsite": event.pay_onsite,
        "privacy": event.privacy,
        "type": event.type,
        "topic": event.topic,
        "sub_topic": event.sub_topic,
        "has_code_of_conduct": event.code_of_conduct != '',
        "code_of_conduct": event.code_of_conduct,
        "copyright": event.copyright.serialize if event.copyright and event.copyright.licence else None,
        "tax_allow": 1 if event.tax_allow else 0,
        "tax": event.tax.serialize if event.tax else None,
        "latitude": event.latitude,
        "longitude": event.longitude,
        "stripe": event.stripe.serialize if event.stripe else None,
        "state": event.state,
        "cheque_details": event.cheque_details,
        "bank_details": event.bank_details,
        "onsite_details": event.onsite_details
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


def save_event_from_json(json, event_id=None):
    """
    Save an event from a wizard json
    :param event_id:
    :param json:
    :return:
    """
    event_data = json['event']
    state = json['state']

    if event_id and represents_int(event_id):
        event = DataGetter.get_event(event_id)
        is_edit = True
    else:
        event = Event()
        is_edit = False

    start_time = get_event_time_field_format(event_data, 'start_time')
    end_time = get_event_time_field_format(event_data, 'end_time')

    if event_data['name'].strip() == '' or not start_time or not end_time:
        abort(400)

    if start_time > end_time:
        abort(400)

    event.name = event_data['name']
    if event_data['event_url'].strip() != "":
        if not event_data['event_url'].startswith("http"):
            event.event_url = "https://" + event_data['event_url']
        else:
            event.event_url = event_data['event_url']
    else:
        event.event_url = ""
    event.location_name = event_data['location_name']
    event.show_map = 1 if event_data['show_map'] else 0
    event.start_time = start_time
    event.end_time = end_time
    event.timezone = event_data['timezone']
    event.description = event_data['description']
    event.privacy = event_data['privacy']
    event.type = event_data['type']
    event.topic = event_data['topic']
    event.sub_topic = event_data['sub_topic']
    event.latitude = event_data['latitude']
    event.longitude = event_data['longitude']
    event.searchable_location_name = get_searchable_location_name(event)
    event.state = state if event_data['location_name'].strip() != '' else 'Draft'

    event.organizer_description = event_data['organizer_description'] if event_data['has_organizer_info'] else ''
    event.organizer_name = event_data['organizer_name'] if event_data['has_organizer_info'] else ''
    event.code_of_conduct = event_data['code_of_conduct'] if event_data['has_code_of_conduct'] else ''

    save_to_db(event, "Event Saved")
    record_activity('create_event', event_id=event.id)
    db.session.add(event)
    db.session.flush()
    db.session.refresh(event)

    copyright = event.copyright
    if not event.copyright:
        copyright = EventCopyright(event=event)

    year = datetime.now().year
    copyright.licence = event_data['copyright']['licence']
    _, _, licence_url, logo, _ = EVENT_LICENCES.get(copyright.licence, ('',) * 5)
    copyright.holder = event.organizer_name
    copyright.year = year
    copyright.logo = logo
    copyright.licence_url = licence_url

    save_social_links(event_data['social_links'], event)

    event.ticket_include = event_data['ticket_include']

    if event.ticket_include:
        event.ticket_url = url_for('event_detail.display_event_tickets', identifier=event.identifier, _external=True)
        save_tickets(event_data['tickets'], event)
    else:
        event.ticket_url = event_data['ticket_url']

    event.discount_code_id = event_data['discount_code_id']
    event.payment_country = event_data['payment_country']
    event.payment_currency = event_data['payment_currency']
    event.pay_by_paypal = event_data['pay_by_paypal']
    event.pay_by_cheque = event_data['pay_by_cheque']
    event.pay_by_bank = event_data['pay_by_bank']
    event.pay_onsite = event_data['pay_onsite']
    event.pay_by_stripe = event_data['pay_by_stripe']

    event.cheque_details = event_data['cheque_details'] if event.pay_by_cheque else ''
    event.bank_details = event_data['bank_details'] if event.pay_by_bank else ''
    event.onsite_details = event_data['onsite_details'] if event.pay_onsite else ''

    if event.pay_by_paypal:
        event.paypal_email = event_data['paypal_email']
    else:
        event.paypal_email = None

    if event.pay_by_stripe and event_data['stripe']['linked']:
        stripe_data = event_data['stripe']
        stripe = event.stripe
        if not stripe:
            stripe = StripeAuthorization(event_id=event.id)

        stripe.stripe_secret_key = stripe_data['stripe_secret_key']
        stripe.stripe_refresh_token = stripe_data['stripe_refresh_token']
        stripe.stripe_publishable_key = stripe_data['stripe_publishable_key']
        stripe.stripe_user_id = stripe_data['stripe_user_id']
        stripe.stripe_email = stripe_data['stripe_email']

        db.session.add(stripe)
    else:
        if event.stripe:
            db.session.delete(event.stripe)

    event.tax_allow = bool(event_data['tax_allow'] == 1)

    if event.tax_allow:
        tax_data = event_data['tax']
        tax = event.tax
        if not tax:
            tax = Tax(event_id=event.id)

        tax.country = tax_data['country']
        tax.tax_name = tax_data['tax_name']
        tax.send_invoice = tax_data['send_invoice']
        tax.tax_id = tax_data['tax_id']
        tax.registered_company = tax_data['registered_company']
        tax.address = tax_data['address']
        tax.state = tax_data['state']
        tax.zip = tax_data['zip']
        tax.tax_include_in_price = tax_data['tax_include_in_price']
        tax.invoice_footer = tax_data['invoice_footer']
        db.session.add(tax)
    else:
        if event.tax:
            db.session.delete(event.tax)

    if event.logo != event_data['logo']:
        if event_data['logo'] and event_data['logo'].strip() != '':
            event.logo = save_logo(event_data['logo'], event.id)
        elif event.logo != '':
            event.logo = ''

    save_to_db(event)

    image_sizes = DataGetter.get_image_sizes_by_type(type='event')
    if not image_sizes:
        image_sizes = ImageSizes(full_width=1300,
                                 full_height=500,
                                 full_aspect='on',
                                 icon_width=75,
                                 icon_height=30,
                                 icon_aspect='on',
                                 thumbnail_width=500,
                                 thumbnail_height=200,
                                 thumbnail_aspect='on',
                                 type='event')
        save_to_db(image_sizes, "Image Sizes Saved")

    if event.background_url != event_data['background_url']:
        if event_data['background_url'] and event_data['background_url'].strip() != '':
            background_url = event_data['background_url']
            jpg_image = convert_background_to_jpg(background_url)
            event.background_url = save_untouched_background(background_url, event.id)
            event.large = save_resized_background(jpg_image, event.id, 'large', image_sizes)
            event.thumbnail = save_resized_background(jpg_image, event.id, 'thumbnail', image_sizes)
            event.icon = save_resized_background(jpg_image, event.id, 'icon', image_sizes)
            os.remove(jpg_image)
            save_to_db(event)
        elif event.background_url != '':
            event.background_url = ''
            event.large = ''
            event.thumbnail = ''
            event.icon = ''
            save_to_db(event)

    if not is_edit:
        role = Role.query.filter_by(name=ORGANIZER).first()
        uer = UsersEventsRoles(login.current_user, event, role)
        if save_to_db(uer, "Event saved"):
            new_email_notification_setting = EmailNotification(next_event=1,
                                                               new_paper=1,
                                                               session_schedule=1,
                                                               session_accept_reject=1,
                                                               user_id=login.current_user.id,
                                                               event_id=event.id)
            save_to_db(new_email_notification_setting, "EmailSetting Saved")

    return {
        'event_id': event.id
    }


def save_tickets(tickets_data, event):
    """
    Save all tickets
    :param tickets_data:
    :param event:
    :return:
    """
    ticket_ids = []
    for ticket_data in tickets_data:
        if ticket_data['id']:
            with db.session.no_autoflush:
                ticket = Ticket.query.filter_by(id=ticket_data['id'], event_id=event.id).first()
                ticket_tags=db.session.query(ticket_tags_table).filter_by(ticket_id=ticket.id)
                if ticket_tags.first():
                    ticket_tags.delete()
        else:
            ticket = Ticket(event=event)

        ticket.name = ticket_data['name']
        ticket.quantity = ticket_data['quantity'] if ticket_data['quantity'] != '' else 100
        ticket.type = ticket_data['type']
        ticket.description_toggle = ticket_data['description_visibility']
        ticket.description = ticket_data['description']
        ticket.price = ticket_data['price'] if ticket_data['price'] != '' and ticket.type == 'paid' else 0
        ticket.hide = ticket_data['ticket_visibility']
        ticket.min_order = ticket_data['min_order'] if ticket_data['min_order'] != '' else 1
        ticket.max_order = ticket_data['max_order'] if ticket_data['max_order'] != '' else 10
        ticket.sales_start = get_event_time_field_format(ticket_data, 'sales_start')
        ticket.sales_end = get_event_time_field_format(ticket_data, 'sales_end')

        if ticket_data['tags_string'].strip() != '':
            tag_names = ticket_data['tags_string'].split(',')
            for tag_name in tag_names:
                tag = TicketTag(name=tag_name, event_id=event.id)
                db.session.add(tag)

        db.session.add(ticket)
        ticket_ids.append(ticket.id)

    with db.session.no_autoflush:
        unwanted_tickets = Ticket.query.filter(~Ticket.id.in_(ticket_ids)).filter_by(event_id=event.id).all()
    for unwanted_ticket in unwanted_tickets:
        if not unwanted_ticket.has_order_tickets():
            db.session.delete(unwanted_ticket)


def save_logo(logo_url, event_id):
    """
    Save the logo
    :param logo_url:
    :param event_id:
    :return:
    """
    upload_path = UPLOAD_PATHS['event']['logo'].format(
        event_id=event_id
    )
    return save_event_image(logo_url, upload_path)


def convert_background_to_jpg(background_url):
    """
    Convert the background image to JPG to reduce the file size
    :param background_url:
    :return:
    """
    file_path = get_path_of_temp_url(background_url)
    im = Image.open(file_path)
    out_im = file_path.replace('png', 'jpg')
    bg = Image.new("RGB", im.size, (255, 255, 255))
    bg.paste(im, (0, 0), im)
    bg.save(out_im, quality=55)
    return out_im


def save_untouched_background(background_url, event_id):
    """
    Save the untouched background image
    :param background_url:
    :param event_id:
    :return:
    """
    upload_path = UPLOAD_PATHS['event']['background_url'].format(
        event_id=event_id
    )
    return save_event_image(background_url, upload_path)


def save_resized_background(background_image_file, event_id, size, image_sizes):
    """
    Save the resized version of the background image
    :param background_image_file:
    :param event_id:
    :param size:
    :param image_sizes:
    :return:
    """

    width_ = 1300
    height_ = 500
    basewidth = image_sizes.full_width
    aspect = image_sizes.full_aspect
    height_size = image_sizes.full_height

    if size == 'large':
        width_ = 1300
        height_ = 500
        aspect = image_sizes.full_aspect
        basewidth = image_sizes.full_width
        height_size = image_sizes.full_height
    elif size == 'thumbnail':
        width_ = 500
        height_ = 200
        aspect = image_sizes.full_aspect
        basewidth = image_sizes.thumbnail_width
        height_size = image_sizes.thumbnail_height
    elif size == 'icon':
        width_ = 75
        height_ = 30
        aspect = image_sizes.icon_aspect
        basewidth = image_sizes.icon_width
        height_size = image_sizes.icon_height

    upload_path = UPLOAD_PATHS['event'][size].format(
        event_id=int(event_id)
    )

    return save_resized_image(background_image_file, width_, height_, basewidth, aspect, height_size, upload_path)


def save_social_links(social_links, event):
    old_social_links = SocialLink.query.filter_by(event_id=event.id)
    for old_social_link in old_social_links:
        flag = 0
        for new_social_link in social_links:
            if old_social_link.name == new_social_link['name'] and new_social_link['link'] != "":
                flag = 1
                break
            else:
                flag = 0
        if flag == 0:
            db.session.delete(old_social_link)
    for social_link in social_links:
        if social_link['link'].strip() != "":
            if not social_link['link'].startswith("http"):
                social_link['link'] = "https://" + social_link['link']
            else:
                social_link['link'] = social_link['link']
            social_exists = SocialLink.query.filter_by(name=social_link['name'], event_id=event.id).scalar()
            if social_exists:
                SocialLink.query.filter_by(name=social_link['name'], event_id=event.id).update({'link': social_link['link']})
            else:
                social = SocialLink(social_link['name'], social_link['link'], event.id)
                db.session.add(social)

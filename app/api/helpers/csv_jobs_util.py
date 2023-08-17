import pytz

from app.api.admin_sales.utils import event_type, summary
from app.api.helpers.group_user_role import get_user_group_role
from app.models import db
from app.models.access_code import AccessCode
from app.models.helpers.versioning import strip_tags
from app.models.order import OrderTicket
from app.models.ticket import access_codes_tickets
from app.models.user_check_in import VirtualCheckIn


def export_orders_csv(orders):
    headers = [
        'Order#',
        'Order Date',
        'Status',
        'Payment Type',
        'Payment Mode',
        'Total Amount',
        'Quantity',
        'Discount Code',
        'Access Code',
        'First Name',
        'Last Name',
        'Email',
        'Tax ID',
        'Address',
        'Company',
        'Country',
        'State',
        'City',
        'Zipcode',
    ]

    rows = [headers]
    for order in orders:
        if order.status != "deleted":
            orderTickets = db.session.query(OrderTicket).filter_by(order_id=order.id)
            access_code_value = ''
            for order_ticket in orderTickets:
                accessCodesTicket = (
                    db.session.query(access_codes_tickets)
                    .filter(access_codes_tickets.c.ticket_id == order_ticket.ticket_id)
                    .first()
                )
                if accessCodesTicket:
                    access_code = (
                        db.session.query(AccessCode)
                        .filter_by(id=accessCodesTicket.access_code_id)
                        .first()
                    )
                    if access_code:
                        access_code_value = access_code.code
                        break

            column = [
                str(order.get_invoice_number()),
                str(order.created_at) if order.created_at else '',
                str(order.status) if order.status else '',
                str(order.paid_via) if order.paid_via else '',
                str(order.payment_mode) if order.payment_mode else '',
                str(order.amount) if order.amount else '',
                str(order.tickets_count),
                str(order.discount_code.code) if order.discount_code else '',
                str(access_code_value),
                str(order.user.first_name)
                if order.user and order.user.first_name
                else '',
                str(order.user.last_name) if order.user and order.user.last_name else '',
                str(order.user.email) if order.user and order.user.email else '',
                str(order.tax_business_info) if order.tax_business_info else '',
                str(order.address) if order.address else '',
                str(order.company) if order.company else '',
                str(order.country) if order.country else '',
                str(order.state) if order.state else '',
                str(order.city) if order.city else '',
                str(order.zipcode) if order.zipcode else '',
            ]
            rows.append(column)

    return rows


def export_attendees_csv(attendees, custom_forms, attendee_form_dict):
    return_dict_list = []

    for attendee in attendees:
        data = {
            'Order#': str(attendee.order.get_invoice_number()) if attendee.order else '-',
            'Order Date': str(attendee.order.created_at.strftime('%B %-d, %Y %H:%M %z'))
            if attendee.order and attendee.order.created_at
            else '-',
            'Status': str(attendee.order.status)
            if attendee.order and attendee.order.status
            else '-',
            'Payment Type': str(attendee.order.paid_via)
            if attendee.order and attendee.order.paid_via
            else '',
            'Payment Mode': str(attendee.order.payment_mode)
            if attendee.order and attendee.order.payment_mode
            else '',
            'Ticket Name': str(attendee.ticket.name)
            if attendee.ticket and attendee.ticket.name
            else '',
            'Ticket Price': str(attendee.ticket.price)
            if attendee.ticket and attendee.ticket.price
            else '0',
            'Ticket Type': str(attendee.ticket.type)
            if attendee.ticket and attendee.ticket.type
            else '',
            'Tax ID': str(attendee.order.tax_business_info)
            if attendee.order.tax_business_info
            else '',
            'Address': str(attendee.order.address) if attendee.order.address else '',
            'Company': str(attendee.order.company) if attendee.order.company else '',
            'Country': str(attendee.order.country) if attendee.order.country else '',
            'State': str(attendee.order.state) if attendee.order.state else '',
            'City': str(attendee.order.city) if attendee.order.city else '',
            'Zipcode': str(attendee.order.zipcode) if attendee.order.zipcode else '',
            'Email': '',
        }

        for field in custom_forms:
            # keys don't match up, for keys like
            # acceptVideoRecording vs accept_video_recording ..
            key_mapping = {}

            for k in attendee_form_dict.keys():
                key_mapping[k.replace("_", "").lower()] = k

            field_raw = field.identifier.replace("_", "").lower()
            key = key_mapping.get(field_raw)
            converted_header = attendee_form_dict.get(key)
            if field.is_complex:
                fields_dict = attendee.complex_field_values
                converted_header = field.name
                data[converted_header] = (
                    fields_dict.get(field.identifier, '') if fields_dict else ''
                )
            else:
                dict_value = getattr(attendee, field.identifier, '')
                dict_value = (
                    "Yes"
                    if str(dict_value) == "True"
                    else "No"
                    if str(dict_value) == "False"
                    else dict_value
                )
                converted_header = field.name
                data[converted_header] = dict_value
        data['virtual_event_checkin_times'] = get_virtual_checkin_times(attendee.id)
        return_dict_list.append(data)

    return return_dict_list


def get_virtual_checkin_times(attendee_id: int):
    """
    get check in times of attendee
    @param attendee_id: attendee_id
    @return: time check in of attendee
    """
    virtual_check_in = VirtualCheckIn.query.filter(
        VirtualCheckIn.ticket_holder_id.any(attendee_id),
        VirtualCheckIn.check_in_type == 'room',
    ).all()
    virtual_check_in_times = [
        item.check_in_at.strftime("%Y-%m-%dT%H:%M:%S%z") for item in virtual_check_in
    ]
    return virtual_check_in_times


def export_sessions_csv(sessions):
    headers = [
        'Session Title',
        'Session Starts At',
        'Session Ends At',
        'Session Speakers',
        'Speaker Emails',
        'Session Track',
        'Session Abstract Short',
        'Session Abstract Long',
        'Comment',
        'Created At',
        'Email Sent',
        'Level',
        'Status',
        'Session Type',
        'Talk Length',
        'Language',
        'Slides',
        'Audio',
        'Video',
        'Average Rating',
        'Number of Ratings',
    ]
    rows = [headers]
    for session in sessions:
        if not session.deleted_at:
            column = [session.title + ' (' + session.state + ')' if session.title else '']
            column.append(
                session.starts_at.astimezone(
                    pytz.timezone(session.event.timezone)
                ).strftime('%B %-d, %Y %H:%M %z')
                if session.starts_at
                else ''
            )
            column.append(
                session.ends_at.astimezone(
                    pytz.timezone(session.event.timezone)
                ).strftime('%B %-d, %Y %H:%M %z')
                if session.ends_at
                else ''
            )
            column.append(
                '; '.join(
                    list(filter(bool, map(lambda sp: sp.name, session.speakers or [])))
                )
            )
            column.append(
                '; '.join(
                    list(filter(bool, map(lambda sp: sp.email, session.speakers or [])))
                )
            )
            column.append(
                session.track.name if session.track and session.track.name else ''
            )
            column.append(
                strip_tags(session.short_abstract) if session.short_abstract else ''
            )
            column.append(
                strip_tags(session.long_abstract) if session.long_abstract else ''
            )
            column.append(strip_tags(session.comments) if session.comments else '')
            column.append(
                session.created_at.strftime('%B %-d, %Y %H:%M %z')
                if session.created_at
                else ''
            )
            column.append('Yes' if session.is_mail_sent else 'No')
            column.append(session.level)
            column.append(session.state)
            column.append(
                session.session_type.name
                if session.session_type and session.session_type.name
                else ''
            )
            column.append(
                session.session_type.length
                if session.session_type and session.session_type.length
                else ''
            )
            column.append(session.language if session.language else '')
            column.append(session.slides_url if session.slides_url else '')
            column.append(session.audio_url if session.audio_url else '')
            column.append(session.video_url if session.video_url else '')
            column.append(session.average_rating)
            column.append(session.rating_count)
            rows.append(column)

    return rows


def export_sales_csv(sales):
    headers = [
        'Event Name',
        'Owner Name',
        'Owner Email',
        'Event Type',
        'Event Date',
        'Ticket (Completed)',
        'Sales (Completed)',
        'Ticket (Placed)',
        'Sales (Placed)',
        'Ticket (Pending)',
        'Sales (Pending)',
    ]
    rows = [headers]
    for sale in sales:
        if not sale.deleted_at:
            column = [sale.name]
            column.append(sale.owner.first_name if sale.owner.first_name else '')
            column.append(sale.owner.email)
            column.append(event_type(sale))
            column.append(
                sale.starts_at.astimezone(pytz.timezone(sale.timezone)).strftime(
                    '%B %-d, %Y %H:%M %z'
                )
                if sale.starts_at
                else ''
            )
            column.append(summary(sale)['completed']['ticket_count'])
            column.append(summary(sale)['completed']['sales_total'])
            column.append(summary(sale)['placed']['ticket_count'])
            column.append(summary(sale)['placed']['sales_total'])
            column.append(summary(sale)['pending']['ticket_count'])
            column.append(summary(sale)['pending']['sales_total'])
            rows.append(column)

    return rows


def export_speakers_csv(speakers):
    headers = [
        'Speaker Name',
        'Speaker Email',
        'Speaker Session(s)',
        'Speaker Mobile',
        'Speaker Bio',
        'Speaker Organisation',
        'Speaker Position',
        'Speaker Experience',
        'Speaker Sponsorship Required',
        'Speaker City',
        'Speaker Country',
        'Speaker Website',
        'Speaker Twitter',
        'Speaker Facebook',
        'Speaker Github',
        'Speaker LinkedIn',
    ]
    rows = [headers]
    for speaker in speakers:
        column = [
            speaker.name if speaker.name else '',
            speaker.email if speaker.email else '',
        ]
        if speaker.sessions:
            session_details = ''
            for session in speaker.sessions:
                if not session.deleted_at:
                    session_details += session.title + ' (' + session.state + '); '
            column.append(session_details[:-2])
        else:
            column.append('')
        column.append(speaker.mobile if speaker.mobile else '')
        column.append(speaker.short_biography if speaker.short_biography else '')
        column.append(speaker.organisation if speaker.organisation else '')
        column.append(speaker.position if speaker.position else '')
        column.append(speaker.speaking_experience if speaker.speaking_experience else '')
        column.append(
            speaker.sponsorship_required if speaker.sponsorship_required else ''
        )
        column.append(speaker.city if speaker.city else '')
        column.append(speaker.country if speaker.country else '')
        column.append(speaker.website if speaker.website else '')
        column.append(speaker.twitter if speaker.twitter else '')
        column.append(speaker.facebook if speaker.facebook else '')
        column.append(speaker.github if speaker.github else '')
        column.append(speaker.linkedin if speaker.linkedin else '')
        rows.append(column)

    return rows


def export_group_followers_csv(followers):
    headers = [
        'Public Profile Name',
        'Email',
        'Group Join Date',
        'Role (Owner, Organizer, Follower)',
    ]
    rows = [headers]
    for follower in followers:
        column = [follower.user.public_name if follower.user.public_name else '']
        column.append(follower.user._email if follower.user._email else '')
        column.append(
            follower.created_at.strftime('%B %-d, %Y %H:%M %z')
            if follower.created_at
            else ''
        )
        column.append(get_user_group_role(follower.user_id, follower.group_id))
        rows.append(column)

    return rows

import pytz

from app.models.helpers.versioning import strip_tags


def export_orders_csv(orders):
    headers = [
        'Order#',
        'Order Date',
        'Status',
        'Payment Type',
        'Total Amount',
        'Quantity',
        'Discount Code',
        'First Name',
        'Last Name',
        'Email',
    ]

    rows = [headers]
    for order in orders:
        if order.status != "deleted":
            column = [
                str(order.get_invoice_number()),
                str(order.created_at) if order.created_at else '',
                str(order.status) if order.status else '',
                str(order.paid_via) if order.paid_via else '',
                str(order.amount) if order.amount else '',
                str(order.tickets_count),
                str(order.discount_code.code) if order.discount_code else '',
                str(order.user.first_name)
                if order.user and order.user.first_name
                else '',
                str(order.user.last_name) if order.user and order.user.last_name else '',
                str(order.user.email) if order.user and order.user.email else '',
            ]
            rows.append(column)

    return rows


def export_attendees_csv(attendees, custom_forms):

    headers = [
        'Order#',
        'Order Date',
        'Status',
        'Payment Type',
        'Ticket Name',
        'Ticket Price',
        'Ticket Type',
    ]

    for fields in custom_forms:
        headers.append(fields.name)

    rows = [headers]

    for attendee in attendees:
        column = [
            str(attendee.order.get_invoice_number()) if attendee.order else '-',
            str(attendee.order.created_at)
            if attendee.order and attendee.order.created_at
            else '-',
            str(attendee.order.status)
            if attendee.order and attendee.order.status
            else '-',
            str(attendee.order.payment_mode)
            if attendee.order and attendee.order.payment_mode
            else '',
            str(attendee.ticket.name) if attendee.ticket and attendee.ticket.name else '',
            str(attendee.ticket.price)
            if attendee.ticket and attendee.ticket.price
            else '0',
            str(attendee.ticket.type) if attendee.ticket and attendee.ticket.type else '',
        ]
        for field in custom_forms:
            if field.is_complex:
                fields_dict = attendee.complex_field_values
                column.append(
                    fields_dict.get(field.identifier, '') if fields_dict else ''
                )
            else:
                column.append(getattr(attendee, field.identifier, ''))

        rows.append(column)

    return rows


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
    ]
    rows = [headers]
    for session in sessions:
        if not session.deleted_at:
            column = [session.title + ' (' + session.state + ')' if session.title else '']
            column.append(
                session.starts_at.astimezone(pytz.timezone(session.event.timezone))
                if session.starts_at
                else ''
            )
            column.append(
                session.ends_at.astimezone(pytz.timezone(session.event.timezone))
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
            column.append(session.created_at if session.created_at else '')
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

from app.models.helpers.versioning import strip_tags


def export_orders_csv(orders):
    headers = ['Order#', 'Order Date', 'Status', 'Payment Type', 'Total Amount', 'Quantity',
               'Discount Code', 'First Name', 'Last Name', 'Email']

    rows = [headers]
    for order in orders:
        if order.status != "deleted":
            column = [str(order.get_invoice_number()), str(order.created_at) if order.created_at else '',
                      str(order.status) if order.status else '', str(order.paid_via) if order.paid_via else '',
                      str(order.amount) if order.amount else '', str(order.tickets_count),
                      str(order.discount_code.code) if order.discount_code else '',
                      str(order.user.first_name)
                      if order.user and order.user.first_name else '',
                      str(order.user.last_name)
                      if order.user and order.user.last_name else '',
                      str(order.user.email) if order.user and order.user.email else '']
            rows.append(column)

    return rows


def export_attendees_csv(attendees):
    headers = ['Order#', 'Order Date', 'Status', 'First Name', 'Last Name', 'Email',
               'Country', 'Payment Type', 'Ticket Name', 'Ticket Price', 'Ticket Type']

    rows = [headers]
    for attendee in attendees:
        column = [str(attendee.order.get_invoice_number()) if attendee.order else '-',
                  str(attendee.order.created_at) if attendee.order and attendee.order.created_at else '-',
                  str(attendee.order.status) if attendee.order and attendee.order.status else '-',
                  str(attendee.firstname) if attendee.firstname else '',
                  str(attendee.lastname) if attendee.lastname else '',
                  str(attendee.email) if attendee.email else '',
                  str(attendee.country) if attendee.country else '',
                  str(attendee.order.payment_mode) if attendee.order and attendee.order.payment_mode else '',
                  str(attendee.ticket.name) if attendee.ticket and attendee.ticket.name else '',
                  str(attendee.ticket.price) if attendee.ticket and attendee.ticket.price else '0',
                  str(attendee.ticket.type) if attendee.ticket and attendee.ticket.type else '']

        rows.append(column)

    return rows


def export_sessions_csv(sessions):
    headers = ['Session Title', 'Session Speakers',
               'Session Track', 'Session Abstract', 'Created At', 'Email Sent',
               'Level', 'Status', 'Session Type', 'Talk Length']
    rows = [headers]
    for session in sessions:
        if not session.deleted_at:
            column = [session.title + ' (' + session.state + ')' if session.title else '']
            if session.speakers:
                in_session = ''
                for speaker in session.speakers:
                    if speaker.name:
                        in_session += (speaker.name + '; ')
                column.append(in_session[:-2])
            else:
                column.append('')
            column.append(session.track.name if session.track and session.track.name else '')
            column.append(strip_tags(session.short_abstract) if session.short_abstract else '')
            column.append(session.created_at if session.created_at else '')
            column.append('Yes' if session.is_mail_sent else 'No')
            column.append(session.level)
            column.append(session.state)
            column.append(session.session_type if session.session_type else '')
            column.append(len(session.long_abstract))
            rows.append(column)

    return rows


def export_speakers_csv(speakers):
    headers = ['Speaker Name', 'Speaker Email', 'Speaker Session(s)',
               'Speaker Mobile', 'Speaker Bio', 'Speaker Organisation', 'Speaker Position']
    rows = [headers]
    for speaker in speakers:
        column = [speaker.name if speaker.name else '', speaker.email if speaker.email else '']
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
        rows.append(column)

    return rows

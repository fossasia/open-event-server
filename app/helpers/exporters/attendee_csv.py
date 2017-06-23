from app.helpers.ticketing import TicketingManager


class AttendeeCsv:

    @staticmethod
    def export(event_id):
        (_, event_id, holders, _, _) = TicketingManager.get_attendee_export_info(event_id=event_id)
        headers = 'Order#,Order Date, Status, First Name, Last Name, Email, Country,' \
            'Payment Type, Ticket Name, Ticket Price, Ticket Type'

        fields = ('order_invoice', 'created_at', 'status', 'firstname', 'lastname', 'email',
                  'country', 'paid_via', 'ticket_name', 'ticket_price', 'ticket_type')
        rows = [headers]
        for holder in holders:
            if holder['status'] != "deleted":
                columns = []
                for f in fields:
                    if type(holder.get(f, '')) == unicode:
                        columns.append(str(holder.get(f, '').encode('utf-8')))
                    else:
                        columns.append(str(holder.get(f, '')))
                rows.append(','.join(columns))

        csv_content = '\n'.join(rows)

        return csv_content

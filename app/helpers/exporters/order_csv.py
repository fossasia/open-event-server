from app.helpers.ticketing import TicketingManager


class OrderCsv:

    @staticmethod
    def export(event_id):
        orders = TicketingManager.get_orders(event_id)
        headers = 'Order#,Order Date, Status, Payment Type, Total Amount, Quantity, Discount Code,' \
            'First Name, Last Name, Email \n'

        rows = [headers]
        for order in orders:
            if order.status != "deleted":
                column = []
                column.append(str(order.get_invoice_number()))
                column.append(str(order.created_at) if order.created_at else '')
                column.append(str(order.status) if order.status else '')
                column.append(str(order.paid_via) if order.paid_via else '')
                column.append(str(order.amount) if order.amount else '')
                column.append(str(order.get_tickets_count()))
                column.append(str(order.discount_code.code) if order.discount_code else '')
                column.append(str(order.user.user_detail.firstname.encode('utf-8'))
                              if order.user.user_detail and order.user.user_detail.firstname else '')
                column.append(str(order.user.user_detail.lastname.encode('utf-8'))
                              if order.user.user_detail and order.user.user_detail.lastname else '')
                column.append(str(order.user.email) if order.user.email else '')
                rows.append(','.join(column))

        csv_content = '\n'.join(rows)

        return csv_content

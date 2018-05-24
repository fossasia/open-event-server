def export_orders_csv(orders):
    headers = ['Order#', 'Order Date', 'Status', 'Payment Type', 'Total Amount', 'Quantity',
               'Discount Code', 'First Name', 'Last Name', 'Email']

    rows = [headers]
    for order in orders:
        if order.status != "deleted":
            column = [str(order.get_invoice_number()), str(order.created_at) if order.created_at else '',
                      str(order.status) if order.status else '', str(order.paid_via) if order.paid_via else '',
                      str(order.amount) if order.amount else '', str(order.get_tickets_count()),
                      str(order.discount_code.code) if order.discount_code else '',
                      str(order.user.first_name)
                      if order.user and order.user.first_name else '',
                      str(order.user.last_name)
                      if order.user and order.user.last_name else '',
                      str(order.user.email) if order.user and order.user.email else '']
            rows.append(column)

    return rows

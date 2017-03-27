# encoding=utf8

import copy
from datetime import datetime, timedelta

from flask import Blueprint
from flask import render_template
from flask import request
from flask import url_for
from flask.ext import login
from werkzeug.exceptions import abort
from werkzeug.utils import redirect

from app import forex
from app.helpers.cached_getter import CachedGetter
from app.helpers.data_getter import DataGetter
from app.helpers.invoicing import InvoicingManager
from app.helpers.payment import get_fee
from app.helpers.ticketing import TicketingManager
from app.models.system_role import CustomSysRole, UserSystemRole
from app.models.user import User
from app.views.super_admin import SALES
from app.views.super_admin import check_accessible, list_navbar

display_currency = 'USD'

sadmin_sales = Blueprint('sadmin_sales', __name__, url_prefix='/admin/sales')


@sadmin_sales.before_request
def verify_accessible():
    return check_accessible(SALES)


@sadmin_sales.route('/')
def index():
    return redirect(url_for('.sales_by_events_view', path='events'))


@sadmin_sales.route('/fees/')
def fees_by_events_view():
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')

    if ('from_date' in request.args and not from_date) or ('to_date' in request.args and not to_date) or \
        ('from_date' in request.args and 'to_date' not in request.args) or \
        ('to_date' in request.args and 'from_date' not in request.args):
        return redirect(url_for('.fees_by_events_view'))

    marketer_role = CustomSysRole.query.filter_by(name='Marketer').first()
    marketer_id = login.current_user.id if login.current_user.is_sys_role(marketer_role.id) else None

    if from_date and to_date:
        orders = TicketingManager.get_orders(
            from_date=datetime.strptime(from_date, '%d/%m/%Y'),
            to_date=datetime.strptime(to_date, '%d/%m/%Y'),
            status='completed',
            marketer_id=marketer_id
        )
    else:
        orders = TicketingManager.get_orders(status='completed', marketer_id=marketer_id)

    events = DataGetter.get_all_events()

    fee_summary = {}
    for event in events:
        fee_summary[str(event.id)] = {
            'name': event.name,
            'payment_currency': event.payment_currency,
            'fee_rate': get_fee(event.payment_currency),
            'fee_amount': 0,
            'tickets_count': 0
        }

    fee_total = 0
    tickets_total = 0

    for order in orders:
        if order.event:
            for order_ticket in order.tickets:
                fee_summary[str(order.event.id)]['tickets_count'] += order_ticket.quantity
                tickets_total += order_ticket.quantity
                ticket = CachedGetter.get_ticket(order_ticket.ticket_id)
                if order.paid_via != 'free' and order.amount > 0 and ticket.price > 0:
                    fee = ticket.price * (get_fee(order.event.payment_currency) / 100)
                    fee = forex(order.event.payment_currency, display_currency, fee)
                    fee_summary[str(order.event.id)]['fee_amount'] += fee
                    fee_total += fee

    return render_template('gentelella/super_admin/sales/fees.html',
                           fee_summary=fee_summary,
                           display_currency=display_currency,
                           from_date=from_date,
                           to_date=to_date,
                           tickets_total=tickets_total,
                           fee_total=fee_total,
                           navigation_bar=list_navbar())


@sadmin_sales.route('/fees/status/')
def fees_status_view():
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')

    if ('from_date' in request.args and not from_date) or ('to_date' in request.args and not to_date) or \
        ('from_date' in request.args and 'to_date' not in request.args) or \
        ('to_date' in request.args and 'from_date' not in request.args):
        return redirect(url_for('.fees_status_view'))

    if from_date and to_date:
        invoices = InvoicingManager.get_invoices(
            from_date=datetime.strptime(from_date, '%d/%m/%Y'),
            to_date=datetime.strptime(to_date, '%d/%m/%Y'),
        )
    else:
        invoices = InvoicingManager.get_invoices()

    return render_template('gentelella/super_admin/sales/fees_status.html',
                           display_currency=display_currency,
                           from_date=from_date,
                           current_date=datetime.now(),
                           overdue_date=datetime.now() + timedelta(days=15),
                           invoices=invoices,
                           to_date=to_date,
                           navigation_bar=list_navbar())


@sadmin_sales.route('/marketer/')
def sales_by_marketer_view(by_discount_code=False):
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')

    if ('from_date' in request.args and not from_date) or ('to_date' in request.args and not to_date) or \
        ('from_date' in request.args and 'to_date' not in request.args) or \
        ('to_date' in request.args and 'from_date' not in request.args):
        return redirect(url_for('.sales_by_marketer_view'))

    orders_summary = {
        'tickets_count': 0,
        'orders_count': 0,
        'total_sales': 0,
        'total_discounts': 0
    }

    tickets_summary = {}

    if not by_discount_code:
        user_roles = UserSystemRole.query.filter(CustomSysRole.name == 'Marketer').all()

        active_users_ids = [x.id for x in user_roles]

        marketers = User.query.filter(User.id.in_(active_users_ids)).all()

        for marketer in marketers:
            tickets_summary[str(marketer.id)] = {
                'email': marketer.email,
                'name': marketer.user_detail.firstname,
                'tickets_count': 0,
                'sales': 0,
                'discounts': 0
            }
    else:
        discount_codes = InvoicingManager.get_discount_codes()
        for discount_code in discount_codes:
            tickets_summary[str(discount_code.id)] = {
                'email': discount_code.code,
                'name': str(discount_code.value) + '% off for ' + str(discount_code.max_quantity) + ' months',
                'tickets_count': 0,
                'sales': 0,
                'discounts': 0,
                'marketer': discount_code.marketer.email
            }

    events = DataGetter.get_all_events_with_discounts()

    for event in events:
        temp_month_summary = {}
        print event
        discount_coupon = CachedGetter.get_discount_code(event.discount_code_id)

        if not by_discount_code:
            key = str(discount_coupon.marketer_id)
        else:
            key = str(discount_coupon.id)

        if from_date and to_date:
            orders = TicketingManager.get_orders(
                from_date=datetime.strptime(from_date, '%d/%m/%Y'),
                to_date=datetime.strptime(to_date, '%d/%m/%Y'),
                status='completed',
                event_id=event.id
            )
        else:
            orders = TicketingManager.get_orders(status='completed', event_id=event.id)

        for order in orders:
            if order.status == 'completed' and order.paid_via != 'free':
                orders_summary['orders_count'] += 1
                key = '{month:02d}{year:d}'.format(month=order.completed_at.month, year=order.completed_at.year)
                temp_month_summary[key] = order.amount
                orders_summary['sales'] += order.amount
                for order_ticket in order.tickets:
                    tickets_summary[key]['tickets_count'] += order_ticket.quantity
                    orders_summary['tickets_count'] += order_ticket.quantity

        # Calculate discount on a monthly basis
        month_count = 1
        for amount in temp_month_summary:
            if discount_coupon.max_quantity <= month_count:
                tickets_summary[key]['discounts'] \
                    += amount * (discount_coupon.value / 100)
                orders_summary['total_discounts'] += amount * (discount_coupon.value / 100)
            month_count += 1

    return render_template('gentelella/super_admin/sales/by_marketer.html',
                           tickets_summary=tickets_summary,
                           display_currency=display_currency,
                           from_date=from_date,
                           to_date=to_date,
                           key_name='marketers' if not by_discount_code else 'discount codes',
                           orders_summary=orders_summary,
                           navigation_bar=list_navbar())


@sadmin_sales.route('/<path>/')
def sales_by_events_view(path):
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')

    if ('from_date' in request.args and not from_date) or ('to_date' in request.args and not to_date) or \
        ('from_date' in request.args and 'to_date' not in request.args) or \
        ('to_date' in request.args and 'from_date' not in request.args):
        return redirect(url_for('.sales_by_events_view', path=path))

    promoted_events = path == 'discounted-events'

    if from_date and to_date:
        orders = TicketingManager.get_orders(
            from_date=datetime.strptime(from_date, '%d/%m/%Y'),
            to_date=datetime.strptime(to_date, '%d/%m/%Y'),
            promoted_event=promoted_events
        )
    else:
        orders = TicketingManager.get_orders(promoted_event=promoted_events)

    if promoted_events:
        events = DataGetter.get_all_events_with_discounts()
    else:
        events = DataGetter.get_all_events()

    orders_summary = {
        'completed': {
            'class': 'success',
            'tickets_count': 0,
            'orders_count': 0,
            'total_sales': 0
        },
        'placed': {
            'class': 'info',
            'tickets_count': 0,
            'orders_count': 0,
            'total_sales': 0
        },
        'pending': {
            'class': 'warning',
            'tickets_count': 0,
            'orders_count': 0,
            'total_sales': 0
        },
        'expired': {
            'class': 'danger',
            'tickets_count': 0,
            'orders_count': 0,
            'total_sales': 0
        },
        'deleted': {
            'class': 'primary',
            'tickets_count': 0,
            'orders_count': 0,
            'total_sales': 0
        },
        'cancelled': {
            'class': 'default',
            'tickets_count': 0,
            'orders_count': 0,
            'total_sales': 0
        }
    }

    tickets_summary_event_wise = {}
    tickets_summary_organizer_wise = {}
    tickets_summary_location_wise = {}

    for event in events:
        tickets_summary_event_wise[str(event.id)] = {
            'name': event.name,
            'payment_currency': event.payment_currency,
            'marketer': '',
            'discount_code': '',
            'live_url': url_for('event_detail.display_event_detail_home', identifier=event.identifier).replace('events',
                                                                                                               'e'),
            'event_url': url_for('events.details_view', event_id=event.id),
            'start_time': event.start_time,
            'end_time': event.end_time,
            'completed': {
                'tickets_count': 0,
                'sales': 0
            },
            'placed': {
                'tickets_count': 0,
                'sales': 0
            },
            'pending': {
                'tickets_count': 0,
                'sales': 0
            },
            'expired': {
                'class': 'danger',
                'tickets_count': 0,
                'sales': 0
            },
            'cancelled': {
                'tickets_count': 0,
                'sales': 0
            },
            'deleted': {
                'tickets_count': 0,
                'sales': 0
            },
        }
        organizer = DataGetter.get_user_event_roles_by_role_name(event.id, 'organizer').first()

        if promoted_events:
            tickets_summary_event_wise[str(event.id)]['marketer'] = \
                event.discount_code.marketer.email
            tickets_summary_event_wise[str(event.id)]['discount_code'] = \
                str(event.discount_code.value) + '% off for ' + str(event.discount_code.max_quantity) + ' months'

        if organizer:
            tickets_summary_organizer_wise[str(organizer.user.id)] = \
                copy.deepcopy(tickets_summary_event_wise[str(event.id)])
            tickets_summary_organizer_wise[str(organizer.user.id)]['name'] = organizer.user.email

        tickets_summary_location_wise[unicode(event.searchable_location_name)] = \
            copy.deepcopy(tickets_summary_event_wise[str(event.id)])
        tickets_summary_location_wise[unicode(event.searchable_location_name)]['name'] = \
            event.searchable_location_name

    for order in orders:
        if order.event:
            if order.status == 'initialized':
                order.status = 'pending'
            orders_summary[str(order.status)]['orders_count'] += 1
            orders_summary[str(order.status)]['total_sales'] += forex(order.event.payment_currency,
                                                                      display_currency, order.amount)
            for order_ticket in order.tickets:
                discount = TicketingManager.get_discount_code(order.event_id, order.discount_code_id)
                orders_summary[str(order.status)]['tickets_count'] += order_ticket.quantity
                ticket = CachedGetter.get_ticket(order_ticket.ticket_id)
                tickets_summary_event_wise[str(order.event_id)][str(order.status)]['tickets_count'] \
                    += order_ticket.quantity
                tickets_summary_organizer_wise[str(organizer.user.id)][str(order.status)]['tickets_count'] \
                    += order_ticket.quantity
                tickets_summary_location_wise[unicode(order.event.searchable_location_name)][str(order.status)][
                    'tickets_count'] \
                    += order_ticket.quantity

                if order.paid_via != 'free' and order.amount > 0:
                    if discount and str(ticket.id) in discount.tickets.split(","):
                        if discount.type == "amount":
                            tickets_summary_event_wise[str(order.event_id)][str(order.status)][
                                'sales'] += forex(order.event.payment_currency, display_currency, \
                                            order_ticket.quantity * (ticket.price - discount.value))
                            tickets_summary_organizer_wise[str(organizer.user.id)][str(order.status)][
                                'sales'] += forex(order.event.payment_currency, display_currency, \
                                            order_ticket.quantity * (ticket.price - discount.value))
                            tickets_summary_location_wise[str(order.event.searchable_location_name)][str(order.status)][
                                'sales'] += forex(order.event.payment_currency, display_currency, \
                                            order_ticket.quantity * (ticket.price - discount.value))
                        else:
                            tickets_summary_event_wise[str(order.event_id)][str(order.status)]['sales'] += \
                                forex(order.event.payment_currency, display_currency, \
                                    order_ticket.quantity * (ticket.price - discount.value * ticket.price / 100.0))
                            tickets_summary_organizer_wise[str(organizer.user.id)][str(order.status)]['sales'] += \
                                forex(order.event.payment_currency, display_currency, \
                                    order_ticket.quantity * (ticket.price - discount.value * ticket.price / 100.0))
                            tickets_summary_location_wise[str(order.event.searchable_location_name)][str(order.status)]['sales'] += \
                                forex(order.event.payment_currency, display_currency, \
                                    order_ticket.quantity * (ticket.price - discount.value * ticket.price / 100.0))
                    else:
                        tickets_summary_event_wise[str(order.event_id)][str(order.status)][
                            'sales'] += forex(order.event.payment_currency, display_currency, order_ticket.quantity * ticket.price)
                        tickets_summary_organizer_wise[str(organizer.user.id)][str(order.status)][
                            'sales'] += forex(order.event.payment_currency, display_currency, order_ticket.quantity * ticket.price)
                        tickets_summary_location_wise[str(order.event.searchable_location_name)][str(order.status)][
                            'sales'] += forex(order.event.payment_currency, display_currency, order_ticket.quantity * ticket.price)
    if path == 'events' or path == 'discounted-events':
        return render_template(
            'gentelella/super_admin/sales/by_events.html',
            tickets_summary=tickets_summary_event_wise,
            display_currency=display_currency,
            from_date=from_date,
            to_date=to_date,
            path=path,
            orders_summary=orders_summary,
            navigation_bar=list_navbar())
    elif path == 'organizers':
        return render_template(
            'gentelella/super_admin/sales/by_organizer.html',
            tickets_summary=tickets_summary_organizer_wise,
            display_currency=display_currency,
            from_date=from_date,
            to_date=to_date,
            path=path,
            orders_summary=orders_summary,
            navigation_bar=list_navbar())
    elif path == 'locations':
        return render_template(
            'gentelella/super_admin/sales/by_location.html',
            tickets_summary=tickets_summary_location_wise,
            display_currency=display_currency,
            from_date=from_date,
            to_date=to_date,
            path=path,
            orders_summary=orders_summary,
            navigation_bar=list_navbar())

    else:
        abort(404)


'''
@sadmin_sales.route('/discount_code/')
def sales_by_discount_code_view():
    return sales_by_marketer_view(True)


@sadmin_sales.route('/discounts/', methods=('GET',))
def discount_codes_view():
    discount_codes = InvoicingManager.get_discount_codes()
    return render_template('gentelella/admin/super_admin/sales/discount_codes.html', discount_codes=discount_codes, navigation_bar=list_navbar())


@sadmin_sales.route('/discounts/create/', methods=('GET', 'POST'))
def discount_codes_create(discount_code_id=None):
    if request.method == 'POST':
        InvoicingManager.create_edit_discount_code(request.form)
        flash("The discount code has been added.", "success")
        return redirect(url_for('.discount_codes_view'))
    discount_code = None
    if discount_code_id:
        discount_code = InvoicingManager.get_discount_code(discount_code_id)

    user_roles = UserSystemRole.query.filter(CustomSysRole.name == 'Marketer').all()

    active_users_ids = [x.id for x in user_roles]

    marketers = User.query.filter(User.id.in_(active_users_ids)).all()

    return render_template('gentelella/admin/super_admin/sales/discount_codes_create.html',
                           discount_code=discount_code, marketers=marketers, navigation_bar=list_navbar())


@sadmin_sales.route('/discounts/check/duplicate/', methods=('GET',))
def check_duplicate_discount_code():
    code = request.args.get('code')
    current = request.args.get('current')
    if not current:
        current = ''
    discount_code = InvoicingManager.get_discount_code(code)
    if (current == "" and discount_code) or (current != "" and discount_code and discount_code.id != int(current)):
        return jsonify({
            "status": "invalid"
        }), 404

    return jsonify({
        "status": "valid"
    }), 200


@sadmin_sales.route('/discounts/<int:discount_code_id>/edit/', methods=('GET', 'POST'))
def discount_codes_edit(discount_code_id=None):
    if not InvoicingManager.get_discount_code(discount_code_id):
        abort(404)
    if request.method == 'POST':
        InvoicingManager.create_edit_discount_code(request.form, discount_code_id)
        flash("The discount code has been edited.", "success")
        return redirect(url_for('.discount_codes_view'))
    return discount_codes_create(discount_code_id)


@sadmin_sales.route('/discounts/<int:discount_code_id>/toggle/', methods=('GET',))
def discount_codes_toggle(discount_code_id=None):
    discount_code = InvoicingManager.get_discount_code(discount_code_id)
    if not discount_code:
        abort(404)
    discount_code.is_active = not discount_code.is_active
    save_to_db(discount_code)
    message = "Activated." if discount_code.is_active else "Deactivated."
    flash("The discount code has been " + message, "success")
    return redirect(url_for('.discount_codes_view'))


@sadmin_sales.route('/discounts/<int:discount_code_id>/delete/', methods=('GET',))
def discount_codes_delete(discount_code_id=None):
    discount_code = InvoicingManager.get_discount_code(discount_code_id)
    if not discount_code:
        abort(404)
    delete_from_db(discount_code, "Discount code deleted")
    flash("The discount code has been deleted.", "warning")
    return redirect(url_for('.discount_codes_view'))
'''

from flask import Blueprint
from flask import render_template

from app.helpers.data_getter import DataGetter
from app.helpers.ticketing import TicketingManager
from app.views.super_admin import EVENTS, check_accessible, list_navbar

sadmin_events = Blueprint('sadmin_events', __name__, url_prefix='/admin/events')


@sadmin_events.before_request
def verify_accessible():
    return check_accessible(EVENTS)


@sadmin_events.route('/')
def index_view():
    live_events = DataGetter.get_all_live_events()
    draft_events = DataGetter.get_all_draft_events()
    past_events = DataGetter.get_all_past_events()
    all_events = DataGetter.get_all_events()
    trash_events = DataGetter.get_trash_events()
    free_ticket_count = {}
    paid_ticket_count = {}
    donation_ticket_count = {}
    max_free_ticket = {}
    max_paid_ticket = {}
    max_donation_ticket = {}
    for event in all_events:
        free_ticket_count[event.id] = TicketingManager.get_orders_count_by_type(event.id, type='free')
        max_free_ticket[event.id] = TicketingManager.get_max_orders_count(event.id, type='free')
        paid_ticket_count[event.id] = TicketingManager.get_orders_count_by_type(event.id, type='paid')
        max_paid_ticket[event.id] = TicketingManager.get_max_orders_count(event.id, type='paid')
        donation_ticket_count[event.id] = TicketingManager.get_orders_count_by_type(event.id, type='donation')
        max_donation_ticket[event.id] = TicketingManager.get_max_orders_count(event.id, type='donation')
    return render_template('gentelella/admin/super_admin/events/events.html',
                           live_events=live_events,
                           draft_events=draft_events,
                           past_events=past_events,
                           all_events=all_events,
                           trash_events=trash_events,
                           free_ticket_count=free_ticket_count,
                           paid_ticket_count=paid_ticket_count,
                           donation_ticket_count=donation_ticket_count,
                           max_free_ticket=max_free_ticket,
                           max_paid_ticket=max_paid_ticket,
                           max_donation_ticket=max_donation_ticket,
                           navigation_bar=list_navbar())

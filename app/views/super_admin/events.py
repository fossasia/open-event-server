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
    all_events_include_trash = all_events + trash_events.all()
    all_ticket_stats = {}
    for event in all_events_include_trash:
        all_ticket_stats[event.id] = TicketingManager.get_ticket_stats(event)
    return render_template('gentelella/super_admin/events/events.html',
                           live_events=live_events,
                           draft_events=draft_events,
                           past_events=past_events,
                           all_events=all_events,
                           trash_events=trash_events,
                           all_ticket_stats=all_ticket_stats,
                           navigation_bar=list_navbar())

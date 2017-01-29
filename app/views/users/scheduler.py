from datetime import datetime

from flask import Blueprint
from flask import render_template
from flask import url_for, flash
from werkzeug.utils import redirect

from app.helpers.data import save_to_db
from app.helpers.data_getter import DataGetter

event_scheduler = Blueprint('event_scheduler', __name__, url_prefix='/events/<event_id>/scheduler')


@event_scheduler.route('/')
def display_view(event_id):
    sessions = DataGetter.get_sessions_by_event_id(event_id)
    event = DataGetter.get_event(event_id)
    if not event.has_session_speakers:
        return render_template('gentelella/users/events/info/enable_module.html', active_page='scheduler',
                               title='Scheduler', event=event)
    return render_template('gentelella/users/events/scheduler/scheduler.html', sessions=sessions, event=event)


@event_scheduler.route('/publish/')
def publish(event_id):
    event = DataGetter.get_event(event_id)
    event.schedule_published_on = datetime.now()
    save_to_db(event, "Event schedule published")
    flash('The schedule has been published for this event', 'success')
    return redirect(url_for('.display_view', event_id=event_id))


@event_scheduler.route('/unpublish/')
def unpublish(event_id):
    event = DataGetter.get_event(event_id)
    event.schedule_published_on = None
    save_to_db(event, "Event schedule unpublished")
    flash('The schedule has been unpublished for this event', 'success')
    return redirect(url_for('.display_view', event_id=event_id))

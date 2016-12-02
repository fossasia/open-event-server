import json
from datetime import datetime

from flask import Blueprint
from flask import make_response
from flask import request, url_for, flash, render_template
from flask.ext import login
from flask.ext.restplus import abort
from markupsafe import Markup
from werkzeug.utils import redirect

from app.helpers.data import DataManager
from app.helpers.data_getter import DataGetter
from app.helpers.export import ExportHelper
from app.models.call_for_papers import CallForPaper


def get_published_event_or_abort(identifier):
    event = DataGetter.get_event_by_identifier(identifier=identifier)
    if not event or event.state != u'Published':
        user = login.current_user
        if not login.current_user.is_authenticated or (not user.is_organizer(event.id) and not
           user.is_coorganizer(event.id) and not
                user.is_track_organizer(event.id)):

            abort(404)

    if event.in_trash:
        abort(404)
    return event


event_detail = Blueprint('event_detail', __name__, url_prefix='/e')


@event_detail.route('/')
def display_default():
    return redirect("/browse")


@event_detail.route('/<identifier>/')
def display_event_detail_home(identifier):
    event = get_published_event_or_abort(identifier)
    placeholder_images = DataGetter.get_event_default_images()
    custom_placeholder = DataGetter.get_custom_placeholders()
    call_for_speakers = DataGetter.get_call_for_papers(event.id).first()
    accepted_sessions = DataGetter.get_sessions(event.id)
    if event.copyright:
        licence_details = DataGetter.get_licence_details(event.copyright.licence)
    else:
        licence_details = None

    module = DataGetter.get_module()
    tickets = DataGetter.get_sales_open_tickets(event.id, True)
    return render_template('gentelella/guest/event/details.html',
                           event=event,
                           placeholder_images=placeholder_images,
                           custom_placeholder=custom_placeholder,
                           accepted_sessions=accepted_sessions,
                           call_for_speakers=call_for_speakers,
                           licence_details=licence_details,
                           module=module,
                           tickets=tickets if tickets else [])


@event_detail.route('/<identifier>/sessions/')
def display_event_sessions(identifier):
    event = get_published_event_or_abort(identifier)
    placeholder_images = DataGetter.get_event_default_images()
    custom_placeholder = DataGetter.get_custom_placeholders()
    if not event.has_session_speakers:
        abort(404)
    call_for_speakers = DataGetter.get_call_for_papers(event.id).first()
    tracks = DataGetter.get_tracks(event.id)
    accepted_sessions = DataGetter.get_sessions(event.id)
    if not accepted_sessions:
        abort(404)
    return render_template('gentelella/guest/event/sessions.html', event=event,
                           placeholder_images=placeholder_images, accepted_sessions=accepted_sessions, tracks=tracks,
                           call_for_speakers=call_for_speakers, custom_placeholder=custom_placeholder)


@event_detail.route('/<identifier>/schedule/')
def display_event_schedule(identifier):
    event = get_published_event_or_abort(identifier)
    placeholder_images = DataGetter.get_event_default_images()
    custom_placeholder = DataGetter.get_custom_placeholders()
    if not event.has_session_speakers:
        abort(404)
    tracks = DataGetter.get_tracks(event.id)
    accepted_sessions = DataGetter.get_sessions(event.id)
    if not accepted_sessions or not event.schedule_published_on:
        abort(404)
    return render_template('gentelella/guest/event/schedule.html', event=event,
                           placeholder_images=placeholder_images, accepted_sessions=accepted_sessions,
                           tracks=tracks, custom_placeholder=custom_placeholder)


@event_detail.route('/<identifier>/schedule/pentabarf.xml')
def display_event_schedule_pentabarf(identifier):
    event = get_published_event_or_abort(identifier)
    if not event.has_session_speakers:
        abort(404)
    accepted_sessions = DataGetter.get_sessions(event.id)
    if not accepted_sessions or not event.schedule_published_on:
        abort(404)

    response = make_response(ExportHelper.export_as_pentabarf(event.id))
    response.headers["Content-Type"] = "application/xml"
    return response


@event_detail.route('/<identifier>/schedule/calendar.ics')
def display_event_schedule_ical(identifier):
    event = get_published_event_or_abort(identifier)
    if not event.has_session_speakers:
        abort(404)
    accepted_sessions = DataGetter.get_sessions(event.id)
    if not accepted_sessions or not event.schedule_published_on:
        abort(404)

    response = make_response(ExportHelper.export_as_ical(event.id))
    response.headers["Content-Type"] = "text/calendar"
    return response


@event_detail.route('/<identifier>/schedule/calendar.xcs')
def display_event_schedule_xcal(identifier):
    event = get_published_event_or_abort(identifier)
    if not event.has_session_speakers:
        abort(404)
    accepted_sessions = DataGetter.get_sessions(event.id)
    if not accepted_sessions or not event.schedule_published_on:
        abort(404)

    response = make_response(ExportHelper.export_as_xcal(event.id))
    response.headers["Content-Type"] = "application/xml"
    return response


@event_detail.route('/<identifier>/cfs/', methods=('GET',))
def display_event_cfs(identifier, via_hash=False):
    event = get_published_event_or_abort(identifier)
    placeholder_images = DataGetter.get_event_default_images()
    custom_placeholder = DataGetter.get_custom_placeholders()
    if not event.has_session_speakers:
        abort(404)

    call_for_speakers = DataGetter.get_call_for_papers(event.id).first()
    accepted_sessions = DataGetter.get_sessions(event.id)

    if not call_for_speakers or (not via_hash and call_for_speakers.privacy == 'private'):
        abort(404)

    form_elems = DataGetter.get_custom_form_elements(event.id)
    speaker_form = json.loads(form_elems.speaker_form)
    session_form = json.loads(form_elems.session_form)

    now = datetime.now()
    state = "now"
    if call_for_speakers.end_date < now:
        state = "past"
    elif call_for_speakers.start_date > now:
        state = "future"
    speakers = DataGetter.get_speakers(event.id).all()
    return render_template('gentelella/guest/event/cfs.html', event=event, accepted_sessions=accepted_sessions,
                           speaker_form=speaker_form,
                           session_form=session_form, call_for_speakers=call_for_speakers,
                           placeholder_images=placeholder_images, state=state, speakers=speakers,
                           via_hash=via_hash, custom_placeholder=custom_placeholder)


@event_detail.route('/cfs/<hash>/', methods=('GET', 'POST'))
def display_event_cfs_via_hash(hash):
    call_for_speakers = CallForPaper.query.filter_by(hash=hash).first()
    if not call_for_speakers:
        abort(404)
    event = DataGetter.get_event(call_for_speakers.event_id)
    placeholder_images = DataGetter.get_event_default_images()
    custom_placeholder = DataGetter.get_custom_placeholders()
    if not event.has_session_speakers:
        abort(404)

    accepted_sessions = DataGetter.get_sessions(event.id)

    if not call_for_speakers:
        abort(404)

    if request.method == 'POST':
        return process_event_cfs(event.identifier)

    form_elems = DataGetter.get_custom_form_elements(event.id)
    speaker_form = json.loads(form_elems.speaker_form)
    session_form = json.loads(form_elems.session_form)

    now = datetime.now()
    state = "now"
    if call_for_speakers.end_date < now:
        state = "past"
    elif call_for_speakers.start_date > now:
        state = "future"
    speakers = DataGetter.get_speakers(event.id).all()
    return render_template('gentelella/guest/event/cfs.html', event=event, accepted_sessions=accepted_sessions,
                           speaker_form=speaker_form,
                           session_form=session_form, call_for_speakers=call_for_speakers,
                           placeholder_images=placeholder_images, state=state, speakers=speakers,
                           via_hash=True, custom_placeholder=custom_placeholder)


@event_detail.route('/<identifier>/cfs/new/', methods=('POST', 'GET'))
def process_event_cfs(identifier, via_hash=False):
    if request.method == 'GET':
        event = get_published_event_or_abort(identifier)
        placeholder_images = DataGetter.get_event_default_images()
        custom_placeholder = DataGetter.get_custom_placeholders()
        if not event.has_session_speakers:
            abort(404)

        call_for_speakers = DataGetter.get_call_for_papers(event.id).first()
        accepted_sessions = DataGetter.get_sessions(event.id)

        if not call_for_speakers or (not via_hash and call_for_speakers.privacy == 'private'):
            abort(404)

        form_elems = DataGetter.get_custom_form_elements(event.id)
        speaker_form = json.loads(form_elems.speaker_form)
        session_form = json.loads(form_elems.session_form)

        now = datetime.now()
        state = "now"
        if call_for_speakers.end_date < now:
            state = "past"
        elif call_for_speakers.start_date > now:
            state = "future"
        speakers = DataGetter.get_speakers(event.id).all()
        return render_template('gentelella/guest/event/cfs_new.html', event=event, accepted_sessions=accepted_sessions,
                               speaker_form=speaker_form,
                               session_form=session_form, call_for_speakers=call_for_speakers,
                               placeholder_images=placeholder_images, state=state, speakers=speakers,
                               via_hash=via_hash, custom_placeholder=custom_placeholder)

    if request.method == 'POST':
        email = request.form['email']
        event = DataGetter.get_event_by_identifier(identifier)
        if not event.has_session_speakers:
            abort(404)
        DataManager.add_session_to_event(request, event.id)
        if login.current_user.is_authenticated:
            flash("Your session proposal has been submitted", "success")
            return redirect(url_for('my_sessions.display_my_sessions_view', event_id=event.id))
        else:
            flash(Markup(
                "Your session proposal has been submitted. Please login/register with <strong><u>" + email + "</u></strong> to manage it."),
                "success")
            return redirect(url_for('admin.login_view', next=url_for('my_sessions.display_my_sessions_view')))


@event_detail.route('/<identifier>/coc/', methods=('GET',))
def display_event_coc(identifier):
    event = get_published_event_or_abort(identifier)
    placeholder_images = DataGetter.get_event_default_images()
    custom_placeholder = DataGetter.get_custom_placeholders()
    accepted_sessions = DataGetter.get_sessions(event.id)
    call_for_speakers = DataGetter.get_call_for_papers(event.id).first()
    if not (event.code_of_conduct and event.code_of_conduct != '' and event.code_of_conduct != ' '):
        abort(404)
    return render_template('gentelella/guest/event/code_of_conduct.html', event=event,
                           placeholder_images=placeholder_images,
                           custom_placeholder=custom_placeholder,
                           accepted_sessions=accepted_sessions,
                           call_for_speakers=call_for_speakers)


@event_detail.route('/<identifier>/tickets/')
def display_event_tickets(identifier):
    event = get_published_event_or_abort(identifier)
    placeholder_images = DataGetter.get_event_default_images()
    custom_placeholder = DataGetter.get_custom_placeholders()
    if event.copyright:
        licence_details = DataGetter.get_licence_details(event.copyright.licence)
    else:
        licence_details = None
    module = DataGetter.get_module()
    tickets = DataGetter.get_sales_open_tickets(event.id, True)
    return render_template('gentelella/guest/event/details.html',
                           event=event,
                           placeholder_images=placeholder_images,
                           custom_placeholder=custom_placeholder,
                           licence_details=licence_details,
                           module=module,
                           tickets=tickets if tickets else [])


# SLUGGED PATHS

@event_detail.route('/<identifier>/<slug>/')
def display_event_detail_home_slugged(identifier, slug):
    return display_event_detail_home(identifier)


@event_detail.route('/<identifier>/<slug>/sessions/')
def display_event_sessions_slugged(identifier, slug):
    return display_event_sessions(identifier)

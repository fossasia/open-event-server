import json

from flask import Blueprint
from flask import url_for, redirect, flash, render_template
from flask.ext import login
from app import db
from app.helpers.data import DataManager, delete_from_db, trash_session as _trash_session, \
    restore_session as _restore_session
from app.helpers.data_getter import DataGetter
from app.helpers.notification_email_triggers import trigger_session_state_change_notifications
from app.helpers.permission_decorators import *

event_sessions = Blueprint('event_sessions', __name__, url_prefix='/events/<int:event_id>/sessions')


def get_session_or_throw(session_id):
    session = DataGetter.get_session(session_id)
    if not session:
        abort(404)
    return session


@event_sessions.route('/')
@can_access
def index_view(event_id):
    sessions = DataGetter.get_sessions_by_event_id(event_id)
    event = DataGetter.get_event(event_id)
    if not event.has_session_speakers:
        return render_template('gentelella/users/events/info/enable_module.html', active_page='sessions',
                               title='Sessions', event=event)
    return render_template('gentelella/users/events/sessions/base_session_table.html',
                           sessions=sessions, event_id=event_id, event=event)


@event_sessions.route('/<int:session_id>/', methods=('GET', 'POST'))
@belongs_to_event
@can_access
def session_display_view(event_id, session_id):
    session = get_session_or_throw(session_id)
    if request.method == 'POST':
        DataManager.edit_session(request, session)
        return redirect(url_for('.index_view', event_id=event_id))
    event = DataGetter.get_event(event_id)
    if not event.has_session_speakers:
        return render_template('gentelella/users/events/info/enable_module.html', active_page='sessions',
                               title='Sessions', event=event)
    form_elems = DataGetter.get_custom_form_elements(event_id)
    if not form_elems:
        flash("Speaker and Session forms have been incorrectly configured for this event."
              " Session creation has been disabled", "danger")
        return redirect(url_for('.index_view', event_id=event_id))
    session_form = json.loads(form_elems.session_form)
    speakers = DataGetter.get_speakers(event_id).all()

    return render_template('gentelella/users/events/sessions/edit.html',
                           session=session, session_form=session_form, event_id=event_id,
                           event=event, speakers=speakers)


@event_sessions.route('/create/', methods=('GET', 'POST'))
@can_access
def create_view(event_id):
    event = DataGetter.get_event(event_id)
    if not event.has_session_speakers:
        return render_template('gentelella/users/events/info/enable_module.html', active_page='sessions',
                               title='Sessions', event=event)
    if request.method == 'POST':
        DataManager.add_session_to_event(request, event_id, use_current_user=False)
        flash("The session and speaker have been saved")
        get_from = request.args.get("from")
        if get_from and get_from == 'speaker':
            return redirect(url_for('event_speakers.index_view', event_id=event_id))
        return redirect(url_for('.index_view', event_id=event_id))

    form_elems = DataGetter.get_custom_form_elements(event_id)
    if not form_elems:
        flash("Speaker and Session forms have been incorrectly configured for this event."
              " Session creation has been disabled", "danger")
        return redirect(url_for('.index_view', event_id=event_id))
    speaker_form = json.loads(form_elems.speaker_form)
    session_form = json.loads(form_elems.session_form)
    speakers = DataGetter.get_speakers(event_id).all()

    return render_template('gentelella/users/events/sessions/new.html',
                           speaker_form=speaker_form, session_form=session_form, event=event, speakers=speakers)


@event_sessions.route('/<int:session_id>/edit/', methods=('GET', 'POST'))
@belongs_to_event
@can_access
def edit_view(event_id, session_id):
    event = DataGetter.get_event(event_id)
    if not event.has_session_speakers:
        return render_template('gentelella/users/events/info/enable_module.html', active_page='sessions',
                               title='Sessions', event=event)

    session = get_session_or_throw(session_id)
    if request.method == 'POST':
        DataManager.edit_session(request, session)
        return redirect(url_for('.index_view', event_id=event_id))

    form_elems = DataGetter.get_custom_form_elements(event_id)
    if not form_elems:
        flash("Speaker and Session forms have been incorrectly configured for this event."
              " Session creation has been disabled", "danger")
        return redirect(url_for('.index_view', event_id=event_id))
    session_form = json.loads(form_elems.session_form)
    speakers = DataGetter.get_speakers(event_id).all()
    return render_template('gentelella/users/events/sessions/edit.html', session=session,
                           session_form=session_form, event=event, speakers=speakers)


@event_sessions.route('/<int:session_id>/invited/', methods=('GET', 'POST'))
@belongs_to_event
def invited_view(event_id, session_id):
    session = DataGetter.get_session(session_id)
    event = DataGetter.get_event(event_id)
    return render_template('gentelella/users/events/sessions/invited.html',
                           session=session, event_id=event_id, event=event)


@event_sessions.route('/<int:session_id>/add_speaker/', methods=('GET', 'POST'))
@belongs_to_event
@can_access
def add_speaker_view(event_id, session_id):
    event = DataGetter.get_event(event_id)
    if not event.has_session_speakers:
        return render_template('gentelella/users/events/info/enable_module.html', active_page='sessions',
                               title='Sessions', event=event)
    form_elems = DataGetter.get_custom_form_elements(event_id)
    if not form_elems:
        flash("Speaker form has been incorrectly configured for this event. Editing has been disabled", "danger")
        return redirect(url_for('.index_view', event_id=event_id))
    speaker_form = json.loads(form_elems.speaker_form)
    if request.method == 'GET':
        return render_template('gentelella/users/events/speakers/edit.html', event_id=event_id,
                               event=event, speaker_form=speaker_form)
    if request.method == 'POST':
        DataManager.add_speaker_to_session(request, event_id, session_id)
        flash("The speaker has been added to session")
        return redirect(url_for('.index_view', event_id=event_id))


@event_sessions.route('/<int:session_id>/accept/', methods=('POST', 'GET'))
@belongs_to_event
@can_accept_and_reject
def accept_session(event_id, session_id):
    session = get_session_or_throw(session_id)
    skip = request.args.get('skip')
    send_email = True
    if skip and skip == 'email':
        send_email = False
    message = request.form.get('message', None) if request.form else None
    subject = request.form.get('subject', None) if request.form else None
    DataManager.session_accept_reject(session, event_id, 'accepted', send_email, message=message, subject=subject)
    return redirect(url_for('.index_view', event_id=event_id))


@event_sessions.route('/<int:session_id>/reject/', methods=('POST', 'GET'))
@belongs_to_event
@can_accept_and_reject
def reject_session(event_id, session_id):
    session = get_session_or_throw(session_id)
    skip = request.args.get('skip')
    send_email = True
    if skip and skip == 'email':
        send_email = False
    message = request.form.get('message', None) if request.form else None
    subject = request.form.get('subject', None) if request.form else None
    DataManager.session_accept_reject(session, event_id, 'rejected', send_email, message=message, subject=subject)
    return redirect(url_for('.index_view', event_id=event_id))

@event_sessions.route('/<int:session_id>/confirm/', methods=('POST', 'GET'))
@belongs_to_event
@can_accept_and_reject
def confirm_session(event_id, session_id):
    session = get_session_or_throw(session_id)
    skip = request.args.get('skip')
    send_email = True
    if skip and skip == 'email':
        send_email = False
    message = request.form.get('message', None) if request.form else None
    subject = request.form.get('subject', None) if request.form else None
    DataManager.session_accept_reject(session, event_id, 'confirmed', send_email, message=message, subject=subject)
    return redirect(url_for('.index_view', event_id=event_id))


@event_sessions.route('/<int:session_id>/send-emails/')
@belongs_to_event
@can_accept_and_reject
def send_emails_session(event_id, session_id):
    session = get_session_or_throw(session_id)
    message = request.form.get('message', None) if request.form else None
    subject = request.form.get('subject', None) if request.form else None
    trigger_session_state_change_notifications(session, event_id, message=message, subject=subject)
    return redirect(url_for('.index_view', event_id=event_id))


@event_sessions.route('/<int:session_id>/trash/')
@belongs_to_event
@can_access
def trash_session(event_id, session_id):
    get_session_or_throw(session_id)
    _trash_session(session_id)
    flash("The session has been deleted", "danger")
    if login.current_user.is_super_admin:
        return redirect(url_for('sadmin_sessions.display_my_sessions_view', event_id=event_id))
    return redirect(url_for('.index_view', event_id=event_id))


@event_sessions.route('/<int:session_id>/restore_trash/')
@belongs_to_event
@can_access
def restore_session(event_id, session_id):
    _restore_session(session_id)
    flash("The session has been restored", "success")
    return redirect(url_for('sadmin_sessions.display_my_sessions_view', event_id=event_id))


@event_sessions.route('/<int:session_id>/delete', methods=('GET',))
@belongs_to_event
@can_access
def delete_session(event_id, session_id):
    session = get_session_or_throw(session_id)
    delete_from_db(session, 'Session Deleted')
    flash("The session has been permanently deleted", "danger")
    return redirect(url_for('sadmin_sessions.display_my_sessions_view', event_id=event_id))


@event_sessions.route('/<int:session_id>/restore/')
@belongs_to_event
@can_access
def restore_session_view(event_id, session_id):
    session = get_session_or_throw(session_id)
    event = DataGetter.get_event(event_id)
    return render_template('gentelella/users/events/sessions/browse_revisions.html',
                           session=session, event_id=event_id, event=event)


@event_sessions.route('/<int:session_id>/restore/<int:version_id>/')
@belongs_to_event
@can_access
def restore_session_revision(event_id, session_id, version_id):
    session = get_session_or_throw(session_id)
    version = session.versions[version_id]
    version.revert()
    db.session.commit()
    flash("The session has been restored.", "success")
    return redirect(url_for('.index_view', event_id=event_id))

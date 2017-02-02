import json
from datetime import datetime

from flask import Blueprint, jsonify
from flask import flash, redirect, url_for, request
from flask import render_template
from flask.ext.restplus import abort
from flask.ext import login
from markupsafe import Markup

from app.helpers.data import DataManager, save_to_db
from app.helpers.data_getter import DataGetter
from app.helpers.auth import AuthManager

my_sessions = Blueprint('my_sessions', __name__, url_prefix='/events/mysessions')


@my_sessions.route('/')
def display_my_sessions_view():
    placeholder_images = DataGetter.get_event_default_images()
    custom_placeholder = DataGetter.get_custom_placeholders()
    upcoming_events_sessions = DataGetter.get_sessions_of_user(upcoming_events=True)
    im_config = DataGetter.get_image_configs()
    im_size = ''
    for config in im_config:
        if config.page == 'mysession':
            im_size = config.size
    past_events_sessions = DataGetter.get_sessions_of_user(upcoming_events=False)
    page_content = {"tab_upcoming_events": "Upcoming Sessions",
                    "tab_past_events": "Past Sessions",
                    "title": "My Session Proposals"}
    if not AuthManager.is_verified_user():
        flash(Markup("Your account is unverified. "
                     "Please verify by clicking on the confirmation link that has been emailed to you."
                     '<br>Did not get the email? Please <a href="/resend_email/" class="alert-link"> '
                     'click here to resend the confirmation.</a>'))
    return render_template('gentelella/users/mysessions/mysessions_list.html',
                           upcoming_events_sessions=upcoming_events_sessions, past_events_sessions=past_events_sessions,
                           page_content=page_content, placeholder_images=placeholder_images,
                           custom_placeholder=custom_placeholder, im_size=im_size)


@my_sessions.route('/<int:session_id>/')
def display_session_view(session_id):
    session = DataGetter.get_sessions_of_user_by_id(session_id)
    if not session:
        abort(404)
    form_elems = DataGetter.get_custom_form_elements(session.event_id)
    if not form_elems:
        flash("Speaker and Session forms have been incorrectly configured for this event."
              " Session creation has been disabled", "danger")
        return redirect(url_for('.display_my_sessions_view', event_id=session.event_id))
    speaker_form = json.loads(form_elems.speaker_form)
    session_form = json.loads(form_elems.session_form)
    event = DataGetter.get_event(session.event_id)
    speakers = DataGetter.get_speakers(session.event_id).all()
    return render_template('gentelella/users/mysessions/mysession_detail.html', session=session,
                           speaker_form=speaker_form, session_form=session_form, event=event, speakers=speakers)


@my_sessions.route('/<int:session_id>/edit/', methods=('POST', 'GET'))
def process_session_view(session_id):
    if request.method == 'GET':
        session = DataGetter.get_sessions_of_user_by_id(session_id)
        if not session:
            abort(404)
        form_elems = DataGetter.get_custom_form_elements(session.event_id)
        if not form_elems:
            flash("Speaker and Session forms have been incorrectly configured for this event."
                  " Session creation has been disabled", "danger")
            return redirect(url_for('.display_my_sessions_view', event_id=session.event_id))
        speaker_form = json.loads(form_elems.speaker_form)
        session_form = json.loads(form_elems.session_form)
        event = DataGetter.get_event(session.event_id)
        speaker = DataGetter.get_speakers(session.event_id).filter_by(user_id=login.current_user.id).first()
        return render_template(
            'gentelella/users/mysessions/mysession_detail_edit.html', session=session,
            photo_delete_url=url_for('.avatar_delete', event_id=event.id, speaker_id=speaker.id),
            speaker_form=speaker_form, session_form=session_form, event=event, speaker=speaker)

    if request.method == 'POST':
        session = DataGetter.get_sessions_of_user_by_id(session_id)
        speaker = DataGetter.get_speakers(session.event_id).filter_by(user_id=login.current_user.id).first()
        DataManager.edit_session(request, session, speaker)
        flash("The session has been updated successfully", "success")
        return redirect(url_for('.display_session_view', session_id=session_id))


@my_sessions.route('/<int:event_id>/speakers/<int:speaker_id>/avatar', methods=('DELETE',))
def avatar_delete(event_id, speaker_id):
    if request.method == 'DELETE':
        speaker = DataGetter.get_speakers(event_id).filter_by(user_id=login.current_user.id, id=speaker_id).first()
        if speaker:
            speaker.photo = ''
            speaker.small = ''
            speaker.thumbnail = ''
            speaker.icon = ''
            save_to_db(speaker)
            return jsonify({'status': 'ok'})
        else:
            abort(403)


@my_sessions.route('/<int:session_id>/withdraw/')
def withdraw_session_view(session_id):
    session = DataGetter.get_sessions_of_user_by_id(session_id)
    session.in_trash = True
    session.trash_date = datetime.now()
    save_to_db(session)
    flash("The session has been withdrawn", "success")
    return redirect(url_for('.display_my_sessions_view', session_id=session_id))

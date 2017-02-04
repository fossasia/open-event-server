import json

from flask import Blueprint
from flask import request, url_for, redirect, flash, jsonify, render_template
from flask.ext.restplus import abort

from app.helpers.data import delete_from_db, save_to_db
from app.helpers.data_getter import DataGetter
from app.helpers.permission_decorators import belongs_to_event
from app.helpers.sessions_speakers.speakers import save_speaker


def get_speaker_or_throw(speaker_id):
    session = DataGetter.get_speaker(speaker_id)
    if not session:
        abort(404)
    return session


event_speakers = Blueprint('event_speakers', __name__, url_prefix='/events/<int:event_id>/speakers')


@event_speakers.route('/')
@belongs_to_event
def index_view(event_id):
    speakers = DataGetter.get_speakers(event_id)
    event = DataGetter.get_event(event_id)
    if not event.has_session_speakers:
        return render_template('gentelella/users/events/info/enable_module.html', active_page='speakers',
                               title='Speakers', event=event)
    return render_template('gentelella/users/events/speakers/base_speaker_table.html',
                           speakers=speakers, event_id=event_id, event=event)


@event_speakers.route('/<int:speaker_id>/edit/', methods=('GET', 'POST'))
@belongs_to_event
def edit_view(event_id, speaker_id):
    speaker = get_speaker_or_throw(speaker_id)
    event = DataGetter.get_event(event_id)
    form_elems = DataGetter.get_custom_form_elements(event_id)
    if not form_elems:
        flash("Speaker form has been incorrectly configured for this event. Editing has been disabled", "danger")
        return redirect(url_for('.index_view', event_id=event_id))
    speaker_form = json.loads(form_elems.speaker_form)
    if request.method == 'GET':
        return render_template('gentelella/users/events/speakers/edit.html',
                               speaker=speaker, event_id=event_id,
                               event=event, speaker_form=speaker_form)
    if request.method == 'POST':
        save_speaker(request, event_id, speaker)
        flash("Speaker has been saved", "success")

    return redirect(url_for('.index_view', event_id=event_id))


@event_speakers.route('/<int:speaker_id>/delete/')
@belongs_to_event
def delete(event_id, speaker_id):
    speaker = get_speaker_or_throw(speaker_id)
    delete_from_db(speaker, 'Speaker Rejected')
    flash("The speaker has been deleted", "danger")
    return redirect(url_for('.index_view', event_id=event_id))


@event_speakers.route('/<int:speaker_id>/avatar/', methods=('DELETE',))
@belongs_to_event
def avatar_delete(event_id, speaker_id):
    if request.method == 'DELETE':
        speaker = DataGetter.get_speaker(speaker_id)
        speaker.photo = ''
        speaker.small = ''
        speaker.thumbnail = ''
        speaker.icon = ''
        save_to_db(speaker)
        return jsonify({'status': 'ok'})

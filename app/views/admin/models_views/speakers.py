import json

from flask.ext.admin import BaseView
from flask.ext.restplus import abort
from flask_admin import expose
from flask.ext import login
from flask import request, url_for, redirect, flash, jsonify
from ....helpers.data import delete_from_db, save_to_db
from ....helpers.data_getter import DataGetter
from ....helpers.storage import upload, UPLOAD_PATHS
from app.helpers.helpers import uploaded_file


def get_speaker_or_throw(speaker_id):
    session = DataGetter.get_speaker(speaker_id)
    if not session:
        abort(404)
    return session


class SpeakersView(BaseView):

    def is_accessible(self):
        return login.current_user.is_authenticated

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('admin.login_view', next=request.url))
        event = DataGetter.get_event(kwargs['event_id'])
        if not event.has_session_speakers:
            return self.render('/gentelella/admin/event/info/enable_module.html', active_page='speakers', title='Speakers', event=event)

    @expose('/')
    def index_view(self, event_id):
        speakers = DataGetter.get_speakers(event_id)
        event = DataGetter.get_event(event_id)
        return self.render('/gentelella/admin/event/speakers/base_speaker_table.html',
                           speakers=speakers, event_id=event_id, event=event)

    @expose('/<int:speaker_id>/edit/', methods=('GET', 'POST'))
    def edit_view(self, event_id, speaker_id):
        speaker = get_speaker_or_throw(speaker_id)
        event = DataGetter.get_event(event_id)
        form_elems = DataGetter.get_custom_form_elements(event_id)
        if not form_elems:
            flash("Speaker form has been incorrectly configured for this event. Editing has been disabled", "danger")
            return redirect(url_for('.index_view', event_id=event_id))
        speaker_form = json.loads(form_elems.speaker_form)
        if request.method == 'GET':
            return self.render('/gentelella/admin/event/speakers/edit.html',
                               speaker=speaker, event_id=event_id,
                               event=event, speaker_form=speaker_form)
        if request.method == 'POST':
            # set photo
            if 'photo' in request.files and request.files['photo'].filename != '':
                speaker_img_file = request.files['photo']
                speaker_img = upload(
                    speaker_img_file,
                    UPLOAD_PATHS['speakers']['photo'].format(
                        event_id=int(event_id), id=int(speaker.id)
                    ))
                speaker.photo = speaker_img
            # set other fields
            speaker.name = request.form.get('name', None)
            speaker.short_biography = request.form.get('short_biography', None)
            speaker.long_biography = request.form.get('long_biography', None)
            speaker.email = request.form.get('email', None)
            speaker.mobile = request.form.get('mobile', None)
            speaker.website = request.form.get('website', None)
            speaker.twitter = request.form.get('twitter', None)
            speaker.facebook = request.form.get('facebook', None)
            speaker.github = request.form.get('github', None)
            speaker.linkedin = request.form.get('linkedin', None)
            speaker.organisation = request.form.get('organisation', None)
            speaker.featured = True if request.form.get('featured', 'false') == 'true' else False
            speaker.position = request.form.get('position', None)
            speaker.country = request.form.get('country', None)
            save_to_db(speaker, "Speaker has been updated")
            flash("Speaker has been saved", "success")

        return redirect(url_for('.index_view', event_id=event_id))

    @expose('/<int:speaker_id>/delete', methods=('GET',))
    def delete(self, event_id, speaker_id):
        speaker = get_speaker_or_throw(speaker_id)
        delete_from_db(speaker, 'Speaker Rejected')
        flash("The speaker has been deleted", "danger")
        return redirect(url_for('.index_view', event_id=event_id))

    @expose('/<int:speaker_id>/photo_upload', methods=('POST',))
    def photo_upload(self, event_id, speaker_id):
        speaker = get_speaker_or_throw(speaker_id)
        event = DataGetter.get_event(event_id)
        photo = request.form['photo']
        if photo:
            photo_file = uploaded_file(file_content=photo)
            photo = upload(
                photo_file,
                UPLOAD_PATHS['speakers']['photo'].format(
                        event_id=int(event_id), id=int(speaker.id)
                ))
            speaker.photo = photo
            save_to_db(speaker)
            return jsonify({'status': 'ok', 'photo': photo})
        else:
            speaker.photo = None
            save_to_db(speaker)
            return jsonify({'status': 'Removed'})

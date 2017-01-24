import json
import shutil
import time
from os import path
from uuid import uuid4

import PIL
from PIL import Image
from flask import Blueprint
from flask import request, url_for, redirect, flash, jsonify, render_template
from flask.ext.restplus import abort

from app.helpers.data import delete_from_db, save_to_db
from app.helpers.data_getter import DataGetter
from app.helpers.helpers import uploaded_file
from app.helpers.storage import upload, upload_local, UPLOAD_PATHS, UploadedFile
from app.models.image_sizes import ImageSizes


def get_speaker_or_throw(speaker_id):
    session = DataGetter.get_speaker(speaker_id)
    if not session:
        abort(404)
    return session


event_speakers = Blueprint('event_speakers', __name__, url_prefix='/events/<int:event_id>/speakers')


@event_speakers.route('/')
def index_view(event_id):
    speakers = DataGetter.get_speakers(event_id)
    event = DataGetter.get_event(event_id)
    if not event.has_session_speakers:
        return render_template('gentelella/admin/event/info/enable_module.html', active_page='speakers',
                               title='Speakers', event=event)
    return render_template('gentelella/admin/event/speakers/base_speaker_table.html',
                           speakers=speakers, event_id=event_id, event=event)


@event_speakers.route('/<int:speaker_id>/edit/', methods=('GET', 'POST'))
def edit_view(event_id, speaker_id):
    speaker = get_speaker_or_throw(speaker_id)
    event = DataGetter.get_event(event_id)
    form_elems = DataGetter.get_custom_form_elements(event_id)
    if not form_elems:
        flash("Speaker form has been incorrectly configured for this event. Editing has been disabled", "danger")
        return redirect(url_for('.index_view', event_id=event_id))
    speaker_form = json.loads(form_elems.speaker_form)
    if request.method == 'GET':
        return render_template('gentelella/admin/event/speakers/edit.html',
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
        logo = request.form.get('photo', None)
        print logo
        if logo != '' and logo:
            filename = '{}.png'.format(time.time())
            filepath = '{}/static/{}'.format(path.realpath('.'),
                                             logo[len('/serve_static/'):])
            logo_file = UploadedFile(filepath, filename)
            print logo_file
            logo = upload(logo_file, 'events/%d/speakers/%d/photo' % (int(event_id), int(speaker.id)))
            speaker.photo = logo
            image_sizes = DataGetter.get_image_sizes_by_type(type='profile')
            if not image_sizes:
                image_sizes = ImageSizes(full_width=150,
                                         full_height=150,
                                         icon_width=35,
                                         icon_height=35,
                                         thumbnail_width=50,
                                         thumbnail_height=50,
                                         type='profile')
            save_to_db(image_sizes, "Image Sizes Saved")
            filename = '{}.jpg'.format(time.time())
            filepath = '{}/static/{}'.format(path.realpath('.'),
                                             logo[len('/serve_static/'):])
            logo_file = UploadedFile(filepath, filename)

            temp_img_file = upload_local(logo_file,
                                         'events/{event_id}/speakers/{id}/temp'.format(
                                             event_id=int(event_id), id=int(speaker.id)))
            temp_img_file = temp_img_file.replace('/serve_', '')

            basewidth = image_sizes.full_width
            img = Image.open(temp_img_file)
            hsize = image_sizes.full_height
            img = img.resize((basewidth, hsize), PIL.Image.ANTIALIAS)
            img.save(temp_img_file)
            file_name = temp_img_file.rsplit('/', 1)[1]
            large_file = UploadedFile(file_path=temp_img_file, filename=file_name)
            profile_thumbnail_url = upload(
                large_file,
                UPLOAD_PATHS['speakers']['thumbnail'].format(
                    event_id=int(event_id), id=int(speaker.id)
                ))

            basewidth = image_sizes.thumbnail_width
            img = Image.open(temp_img_file)
            hsize = image_sizes.thumbnail_height
            img = img.resize((basewidth, hsize), PIL.Image.ANTIALIAS)
            img.save(temp_img_file)
            file_name = temp_img_file.rsplit('/', 1)[1]
            thumbnail_file = UploadedFile(file_path=temp_img_file, filename=file_name)
            profile_small_url = upload(
                thumbnail_file,
                UPLOAD_PATHS['speakers']['small'].format(
                    event_id=int(event_id), id=int(speaker.id)
                ))

            basewidth = image_sizes.icon_width
            img = Image.open(temp_img_file)
            hsize = image_sizes.icon_height
            img = img.resize((basewidth, hsize), PIL.Image.ANTIALIAS)
            img.save(temp_img_file)
            file_name = temp_img_file.rsplit('/', 1)[1]
            icon_file = UploadedFile(file_path=temp_img_file, filename=file_name)
            profile_icon_url = upload(
                icon_file,
                UPLOAD_PATHS['speakers']['icon'].format(
                    event_id=int(event_id), id=int(speaker.id)
                ))
            shutil.rmtree(path='static/media/' + 'events/{event_id}/speakers/{id}/temp'.format(
                event_id=int(event_id), id=int(speaker.id)))
            speaker.thumbnail = profile_thumbnail_url
            speaker.small = profile_small_url
            speaker.icon = profile_icon_url
            save_to_db(speaker, "Speaker photo saved")
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
        speaker.city = request.form.get('city', None)
        if request.form.get('heard_from', None) == "Other":
            speaker.heard_from =  request.form.get('other_text', None)
        else:
            speaker.heard_from =  request.form.get('heard_from', None)
        speaker.sponsorship_required = request.form.get('sponsorship_required', None)
        speaker.speaking_experience = request.form.get('speaking_experience', None)
        save_to_db(speaker, "Speaker has been updated")
        flash("Speaker has been saved", "success")

    return redirect(url_for('.index_view', event_id=event_id))


@event_speakers.route('/<int:speaker_id>/delete', methods=('GET',))
def delete(event_id, speaker_id):
    speaker = get_speaker_or_throw(speaker_id)
    delete_from_db(speaker, 'Speaker Rejected')
    flash("The speaker has been deleted", "danger")
    return redirect(url_for('.index_view', event_id=event_id))


@event_speakers.route('/<int:speaker_id>/photo_upload', methods=('POST',))
def photo_upload(event_id, speaker_id):
    speaker = get_speaker_or_throw(speaker_id)
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


@event_speakers.route('/<int:speaker_id>/editfiles/bgimage', methods=('POST', 'DELETE'))
def bgimage_upload(event_id, speaker_id):
    if request.method == 'POST':
        background_image = request.form['bgimage']
        if background_image:
            background_file = uploaded_file(file_content=background_image)
            background_url = upload(
                background_file,
                UPLOAD_PATHS['speakers']['photo'].format(
                    event_id=int(event_id), id=int(speaker_id)
                ))
            return jsonify({'status': 'ok', 'background_url': background_url})
        else:
            return jsonify({'status': 'no bgimage'})
    elif request.method == 'DELETE':
        speaker = DataGetter.get_speaker(int(speaker_id))
        speaker.photo = ''
        save_to_db(speaker)
        return jsonify({'status': 'ok'})


@event_speakers.route('/create/files/bgimage', methods=('POST',))
def create_event_bgimage_upload(event_id):
    if request.method == 'POST':
        background_image = request.form['bgimage']
        if background_image:
            background_file = uploaded_file(file_content=background_image)
            background_url = upload_local(
                background_file,
                UPLOAD_PATHS['temp']['event'].format(uuid=uuid4())
            )
            return jsonify({'status': 'ok', 'background_url': background_url})
        else:
            return jsonify({'status': 'no bgimage'})

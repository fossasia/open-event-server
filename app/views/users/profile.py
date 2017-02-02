from uuid import uuid4

from flask import Blueprint
from flask import render_template
from flask import request, url_for, redirect, flash, jsonify
from flask.ext import login
from markupsafe import Markup

from app.helpers.auth import AuthManager
from app.helpers.data import DataManager, get_facebook_auth, get_instagram_auth, get_twitter_auth_url, save_to_db, get_google_auth
from app.helpers.data_getter import DataGetter
from app.helpers.helpers import uploaded_file
from app.helpers.oauth import FbOAuth, InstagramOAuth, OAuth
from app.helpers.storage import upload, UPLOAD_PATHS, upload_local

profile = Blueprint('profile', __name__, url_prefix='/profile')


@profile.route('/')
def index_view():
    if not AuthManager.is_verified_user():
        flash(Markup("Your account is unverified. "
                     "Please verify by clicking on the confirmation link that has been emailed to you."
                     '<br>Did not get the email? Please <a href="/resend_email/" class="alert-link"> '
                     'click here to resend the confirmation.</a>'))
    profile = DataGetter.get_user(login.current_user.id)
    return render_template('gentelella/users/profile/index.html',
                           profile=profile)


@profile.route('/edit/', methods=('GET', 'POST'))
@profile.route('/edit/<user_id>/', methods=('GET', 'POST'))
def edit_view(user_id=None):
    admin = None
    if not user_id:
        user_id = login.current_user.id
    else:
        admin = True
    if request.method == 'POST':
        DataManager.update_user(request.form, int(user_id))
        if admin:
            return redirect(url_for('sadmin_users.details_view', user_id=user_id))
        return redirect(url_for('.index_view'))
    return redirect(url_for('.index_view'))


@profile.route('/fb_connect/', methods=('GET', 'POST'))
def connect_facebook():
    facebook = get_facebook_auth()
    fb_auth_url, state = facebook.authorization_url(FbOAuth.get_auth_uri(), access_type='offline')
    return redirect(fb_auth_url)


@profile.route('/tw_connect/', methods=('GET', 'POST'))
def connect_twitter():
    twitter_auth_url, __ = get_twitter_auth_url()
    return redirect('https://api.twitter.com/oauth/authenticate?' + twitter_auth_url)


@profile.route('/instagram_connect/', methods=('GET', 'POST'))
def connect_instagram():
    instagram = get_instagram_auth()
    instagram_auth_url, state = instagram.authorization_url(InstagramOAuth.get_auth_uri(), access_type='offline')
    return redirect(instagram_auth_url)


@profile.route('/<int:user_id>/editfiles/bgimage/', methods=('POST', 'DELETE'))
def bgimage_upload(user_id):
    if request.method == 'POST':
        background_image = request.form['bgimage']
        if background_image:
            background_file = uploaded_file(file_content=background_image)
            background_url = upload(
                background_file,
                UPLOAD_PATHS['user']['avatar'].format(
                    user_id=user_id
                ))
            return jsonify({'status': 'ok', 'background_url': background_url})
        else:
            return jsonify({'status': 'no bgimage'})
    elif request.method == 'DELETE':
        profile = DataGetter.get_user(int(user_id))
        profile.avatar_uploaded = ''
        save_to_db(profile)
        return jsonify({'status': 'ok'})


@profile.route('/create/files/bgimage/', methods=('POST',))
def create_event_bgimage_upload():
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

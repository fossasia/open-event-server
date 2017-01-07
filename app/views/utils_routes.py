from __future__ import print_function
import json
import os

import geoip2.database
from flask import Blueprint, current_app
from flask import flash
from flask import jsonify, url_for, redirect, request, send_from_directory, \
    render_template, make_response
from flask.ext import login
from flask.ext.migrate import upgrade
from requests.exceptions import HTTPError

from app.helpers.flask_helpers import get_real_ip, slugify
from app.helpers.oauth import OAuth, FbOAuth, InstagramOAuth, TwitterOAuth
from app.helpers.storage import upload
from ..helpers.data import get_google_auth, create_user_oauth, get_facebook_auth, user_logged_in, get_instagram_auth
from ..helpers.data import save_to_db, uploaded_file_provided_by_url
from ..helpers.data_getter import DataGetter
from ..helpers.helpers import get_serializer

utils_routes = Blueprint('', __name__)


@utils_routes.route('/gCallback/', methods=('GET', 'POST'))
def callback():
    if login.current_user is not None and login.current_user.is_authenticated:
        return redirect(url_for('admin.index'))
    elif 'error' in request.args:
        if request.args.get('error') == 'access denied':
            login.logout_user()
            flash("You denied access during login.")
            return redirect(url_for('admin.login_view'))
        login.logout_user()
        flash("OAuth Authorization error. Please try again later.")
        return redirect(url_for('admin.login_view'))
    elif 'code' not in request.args and 'state' not in request.args:
        login.logout_user()
        return redirect(url_for('admin.login_view'))
    else:
        google = get_google_auth()
        state = google.authorization_url(OAuth.get_auth_uri(), access_type='offline')[1]
        google = get_google_auth(state=state)
        code_url = None
        if 'code' in request.args:
            code_url = request.args.get('code')
        try:
            token = google.fetch_token(OAuth.get_token_uri(), authorization_url=request.url,
                                       code=code_url, client_secret=OAuth.get_client_secret())
        except HTTPError:
            flash("OAuth Authorization error. Please try again later.")
            return redirect(url_for('admin.login_view'))
        google = get_google_auth(token=token)
        resp = google.get(OAuth.get_user_info())
        if resp.status_code == 200:
            user_data = resp.json()
            email = user_data['email']
            user = DataGetter.get_user_by_email(email, no_flash=True)
            user = create_user_oauth(user, user_data, token=token, method='Google')
            if user.password is None:
                s = get_serializer()
                email = s.dumps(user.email)
                return redirect(url_for('admin.create_password_after_oauth_login', email=email))
            else:
                login.login_user(user)
                user_logged_in(user)
                return redirect(intended_url())
        login.logout_user()
        flash("OAuth Authorization error. Please try again later.")
        return redirect(url_for('admin.login_view'))


@utils_routes.route('/fCallback/', methods=('GET', 'POST'))
def facebook_callback():
    if login.current_user is not None and login.current_user.is_authenticated:
        try:
            facebook, __ = get_fb_auth()
            response = facebook.get(FbOAuth.get_user_info())
            if response.status_code == 200:
                user_info = response.json()
                update_user_details(first_name=user_info['first_name'],
                                    last_name=user_info['last_name'],
                                    facebook_link=user_info['link'],
                                    file_url=user_info['picture']['data']['url'])
        except Exception:
            pass
        return redirect(url_for('admin.index'))
    elif 'error' in request.args:
        if request.args.get('error') == 'access denied':
            flash("You denied access during login.")
            return redirect(url_for('admin.login_view'))
        login.logout_user()
        flash("OAuth Authorization error. Please try again later.")
        return redirect(url_for('admin.login_view'))
    elif 'code' not in request.args and 'state' not in request.args:
        login.logout_user()
        return redirect(url_for('admin.login_view'))
    else:
        facebook, token = get_fb_auth()
        response = facebook.get(FbOAuth.get_user_info())
        if response.status_code == 200:
            user_info = response.json()
            email = user_info['email']
            user_email = DataGetter.get_user_by_email(email, no_flash=True)
            user = create_user_oauth(user_email, user_info, token=token, method='Facebook')
            if user.password is None:
                s = get_serializer()
                email = s.dumps(user.email)
                return redirect(url_for('admin.create_password_after_oauth_login', email=email))
            else:
                login.login_user(user)
                user_logged_in(user)
                return redirect(intended_url())
        flash("OAuth Authorization error. Please try again later.")
        login.logout_user()
        return redirect(url_for('admin.login_view'))


def update_user_details(first_name=None, last_name=None, facebook_link=None, twitter_link=None, file_url=None):
    user = login.current_user
    if not user.user_detail.facebook:
        user.user_detail.facebook = facebook_link
    if not user.user_detail.firstname:
        user.user_detail.firstname = first_name
    if not user.user_detail.lastname:
        user.user_detail.lastname = last_name
    if not user.user_detail.avatar_uploaded:
        filename, img = uploaded_file_provided_by_url(file_url)
        background_url = upload(img, '/image/' + filename)
        user.user_detail.avatar_uploaded = background_url
    if not user.user_detail.twitter:
        user.user_detail.twitter = twitter_link
    save_to_db(user)


def get_fb_auth():
    facebook = get_facebook_auth()
    state = facebook.authorization_url(FbOAuth.get_auth_uri(), access_type='offline')[1]
    facebook = get_facebook_auth(state=state)
    code_url = None
    if 'code' in request.args:
        code_url = request.args.get('code')
    try:
        token = facebook.fetch_token(FbOAuth.get_token_uri(), authorization_url=request.url,
                                     code=code_url, client_secret=FbOAuth.get_client_secret())
    except HTTPError:
        return 'HTTP Error occurred'
    return get_facebook_auth(token=token), token


@utils_routes.route('/tCallback/', methods=('GET', 'POST'))
def twitter_callback():
    oauth_verifier = request.args.get('oauth_verifier', '')
    oauth_token = request.args.get('oauth_token', '')
    client, access_token = TwitterOAuth().get_authorized_client(oauth_verifier,
                                                                oauth_token)
    resp, content = client.request(
        "https://api.twitter.com/1.1/users/show.json?screen_name=" + access_token["screen_name"] + "&user_id=" +
        access_token["user_id"], "GET")
    user_info = json.loads(content)
    update_user_details(first_name=user_info['name'],
                        file_url=user_info['profile_image_url'],
                        twitter_link="https://twitter.com/" + access_token["screen_name"])
    return redirect(url_for('profile.index_view'))


@utils_routes.route('/iCallback/', methods=('GET', 'POST'))
def instagram_callback():
    instagram = get_instagram_auth()
    state = instagram.authorization_url(InstagramOAuth.get_auth_uri(), access_type='offline')
    instagram = get_instagram_auth(state=state)
    if 'code' in request.url:
        code_url = (((request.url.split('&'))[0]).split('='))[1]
        token = instagram.fetch_token(InstagramOAuth.get_token_uri(),
                                      authorization_url=request.url,
                                      code=code_url,
                                      client_secret=InstagramOAuth.get_client_secret())
        response = instagram.get(
            'https://api.instagram.com/v1/users/self/media/recent/?access_token=' + token.get('access_token',
                                                                                              '')).json()
        for el in response.get('data'):
            filename, uploaded_file = uploaded_file_provided_by_url(el['images']['standard_resolution']['url'])
            upload(uploaded_file, '/image/' + filename)

    flash("OAuth Authorization error. Please try again later.")
    return redirect(url_for('admin.login_view'))


@utils_routes.route('/pic/<path:filename>')
def send_pic(filename):
    """Returns image"""
    return send_from_directory(os.path.realpath('.') + '/static/', filename)


@utils_routes.route('/calendar/<path:filename>')
def send_cal(filename):
    """Returns calendar"""
    return send_from_directory(os.path.realpath('.') + '/static/', filename)


@utils_routes.route('/serve_static/<path:filename>')
def serve_static(filename):
    """
    Sends static file
    Note - This is not the most efficient method but since only development
    system will be using it, it's OK.
    Static files in production are stored on AWS so this won't be used
    """
    return send_from_directory(current_app.config['BASE_DIR'] + '/static/', filename)


@utils_routes.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.dirname(os.path.dirname(__file__)) + '/static/', 'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


@utils_routes.route('/health-check/')
def health_check():
    return jsonify({
        "status": "ok"
    })


@utils_routes.route('/healthz/')
def healthz_check():
    return health_check()


@utils_routes.route('/healthz')
def healthz_check_no_slash():
    return health_check()


@utils_routes.route('/api/location/', methods=('GET', 'POST'))
def location():
    ip = get_real_ip(True)

    try:
        reader = geoip2.database.Reader(os.path.realpath('.') + '/static/data/GeoLite2-Country.mmdb')
        response = reader.country(ip)
        return jsonify({
            'status': 'ok',
            'name': response.country.name,
            'code': response.country.iso_code,
            'slug': slugify(response.country.name),
            'ip': ip
        })
    except:
        return jsonify({
            'status': 'ok',
            'silent_error': 'look_up_failed',
            'name': 'United States',
            'slug': slugify('United States'),
            'code': 'US',
            'ip': ip
        })


@utils_routes.route('/migrate/', methods=('GET', 'POST'))
def run_migrations():
    try:
        upgrade()
    except:
        print("Migrations have been run")
    return jsonify({'status': 'ok'})


def intended_url():
    return request.args.get('next') or url_for('admin.index')


@utils_routes.route('/robots.txt', methods=('GET', 'POST'))
def robots_txt():
    resp = make_response(render_template('robots.txt'))
    resp.headers['Content-type'] = 'text/plain'
    return resp

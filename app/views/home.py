import logging
import os
import random
import string
import urllib
from urllib2 import urlopen

import geoip2.database
from flask import Blueprint
from flask import abort, render_template, current_app
from flask import url_for, redirect, request, session, flash
from flask.ext import login
from flask.ext.login import login_required
from flask.ext.scrypt import generate_password_hash

from app.helpers.data import DataManager, save_to_db, get_google_auth, get_facebook_auth, create_user_password, \
    user_logged_in, record_activity
from app.helpers.data_getter import DataGetter
from app.helpers.flask_ext.helpers import get_real_ip, slugify
from app.helpers.helpers import send_email_with_reset_password_hash, send_email_confirmation, \
    get_serializer, get_request_stats
from app.helpers.oauth import OAuth, FbOAuth
from app.models.user import User
from app.views.public.explore import erase_from_dict


def intended_url():
    return request.args.get('next') or url_for('.index')


def record_user_login_logout(template, user):
    req_stats = get_request_stats()
    record_activity(
        template,
        user=user,
        **req_stats
    )


def str_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


home_routes = Blueprint('admin', __name__)


@home_routes.route('/')
def index():
    call_for_speakers_events = DataGetter.get_call_for_speakers_events()
    upcoming_events = DataGetter.get_all_published_events().limit(12).all()
    placeholder_images = DataGetter.get_event_default_images()
    custom_placeholder = DataGetter.get_custom_placeholders()
    im_config = DataGetter.get_image_configs()
    im_size = ''
    for config in im_config:
        if config.page == 'front':
            im_size = config.size
    return render_template('gentelella/guest/home.html',
                           call_for_speakers_events=call_for_speakers_events,
                           upcoming_events=upcoming_events,
                           placeholder_images=placeholder_images,
                           custom_placeholder=custom_placeholder,
                           im_size=im_size)


@home_routes.route('/login/', methods=('GET', 'POST'))
def login_view():
    if login.current_user.is_authenticated:
        return redirect(url_for('.index'))

    if request.method == 'GET':
        google = get_google_auth()
        auth_url, state = google.authorization_url(OAuth.get_auth_uri(), access_type='offline')
        session['oauth_state'] = state

        # Add Facebook Oauth 2.0 login
        facebook = get_facebook_auth()
        fb_auth_url, state = facebook.authorization_url(FbOAuth.get_auth_uri(), access_type='offline')
        session['fb_oauth_state'] = state
        return render_template('gentelella/users/login/login.html', auth_url=auth_url, fb_auth_url=fb_auth_url)
    if request.method == 'POST':
        email = request.form['email']
        user = DataGetter.get_user_by_email(email)
        if user is None:
            logging.info('No such user')
            return redirect(url_for('admin.login_view'))
        if user.password != generate_password_hash(request.form['password'], user.salt):
            logging.info('Password Incorrect')
            flash('Incorrect Password', 'danger')
            return redirect(url_for('admin.login_view'))
        login.login_user(user)
        record_user_login_logout('user_login', user)

        # Store user_id in session for socketio use
        session['user_id'] = login.current_user.id

        logging.info('logged successfully')
        user_logged_in(user)
        return redirect(intended_url())


@home_routes.route('/register/', methods=('GET', 'POST'))
def register_view():
    if request.method == 'GET':
        return render_template('gentelella/users/login/register.html')
    if request.method == 'POST':
        logging.info("Registration under process")
        s = get_serializer()
        data = [request.form['email'], request.form['password']]
        user = DataManager.create_user(data)
        form_hash = s.dumps([request.form['email'], str_generator()])
        link = url_for('.create_account_after_confirmation_view', hash=form_hash, _external=True)
        send_email_confirmation(request.form, link)
        login.login_user(user)
        record_user_login_logout('user_login', user)
        logging.info('logged successfully')
        user_logged_in(user)
        return redirect(intended_url())


@home_routes.route('/resend/', methods=('GET',))
@login_required
def resend_email_confirmation():
    user = login.current_user
    if not user.is_verified:
        s = get_serializer()
        email = user.email
        form_hash = s.dumps([email, str_generator()])
        link = url_for('.create_account_after_confirmation_view', hash=form_hash, _external=True)
        data = {
            "email": email
        }
        send_email_confirmation(data, link)
        flash('Confirmation email has been sent again.', 'info')
    else:
        flash('Your email has already been confirmed.', 'info')
    return redirect(url_for('events.index_view'))


@home_routes.route('/account/create/<hash>/')
def create_account_after_confirmation_view(hash):
    s = get_serializer()
    data = s.loads(hash)
    user = User.query.filter_by(email=data[0]).first()
    user.is_verified = True
    save_to_db(user, 'User updated')
    login.login_user(user)
    record_user_login_logout('user_login', user)
    user_logged_in(user)
    flash('Thank you. Your new email is now confirmed', 'success')
    return redirect(url_for('settings.contact_info_view'))


@home_routes.route('/password/new/<email>/', methods=('GET', 'POST'))
def create_password_after_oauth_login(email):
    s = get_serializer()
    email = s.loads(email)
    user = DataGetter.get_user_by_email(email)
    if request.method == 'GET':
        return render_template('gentelella/users/login/create_password.html')
    if request.method == 'POST':
        user = create_user_password(request.form, user)
        if user is not None:
            login.login_user(user)
            record_user_login_logout('user_login', user)
            user_logged_in(user)
            return redirect(intended_url())


@home_routes.route('/password/reset/', methods=('GET', 'POST'))
def password_reset_view():
    """Password reset view"""
    if request.method == 'GET':
        return render_template('gentelella/users/login/password_reminder.html')
    if request.method == 'POST':
        email = request.form['email']
        user = DataGetter.get_user_by_email(email)
        if user:
            link = request.host + url_for(".change_password_view", hash=user.reset_password)
            send_email_with_reset_password_hash(email, link)
            flash('Please go to the link sent to your email to reset your password')
        return redirect(url_for('.login_view'))


@home_routes.route('/reset_password/<hash>/', methods=('GET', 'POST'))
def change_password_view(hash):
    """Change password view"""
    if request.method == 'GET':
        return render_template('gentelella/users/login/change_password.html')
    if request.method == 'POST':
        DataManager.reset_password(request.form, hash)
        return redirect(url_for('.index'))


@home_routes.route('/logout/')
@login_required
def logout_view():
    """Logout method which redirect to index"""
    record_user_login_logout('user_logout', login.current_user)
    login.logout_user()
    return redirect(url_for('.index'))


@home_routes.route('/set_role/', methods=('GET', 'POST'))
@login_required
def set_role():
    """Set user role method"""
    id = request.args['id']
    role = request.args['roles']
    user = DataGetter.get_user(id)
    user.role = role
    save_to_db(user, "User Role updated")
    return redirect(url_for('.roles_manager'))


@home_routes.route('/forbidden/')
def forbidden_view():
    return render_template('gentelella/errors/403.html')


@home_routes.route('/browse/')
def browse_view():
    params = request.args.items()
    params = dict((k, v) for k, v in params if v)

    def test_and_remove(key):
        if request.args.get(key) and request.args.get("query"):
            if request.args.get(key).lower() == request.args.get("query").lower():
                erase_from_dict(params, 'query')

    if not request.args.get("location"):
        try:
            reader = geoip2.database.Reader(
                os.path.abspath(current_app.config['BASE_DIR'] + '/static/data/GeoLite2-Country.mmdb'))
            ip = get_real_ip()
            if ip == '127.0.0.1' or ip == '0.0.0.0':
                ip = urlopen('http://ip.42.pl/raw').read()  # On local test environments
            response = reader.country(ip)
            country = response.country.name
        except:
            country = "United States"
    else:
        country = request.args.get("location")

    test_and_remove("location")
    test_and_remove("category")
    erase_from_dict(params, 'location')

    return redirect(url_for('explore.explore_view', location=slugify(country)) + '?' + urllib.urlencode(params))


@home_routes.route('/check_email/', methods=('POST', 'GET'))
def check_duplicate_email():
    if request.method == 'GET':
        email = request.args['email']
        user = DataGetter.get_user_by_email(email, no_flash=True)
        if user is None:
            return '200 OK'
        else:
            return abort(404)


@home_routes.route('/resend_email/')
def resend_email_confirmation_old():
    return resend_email_confirmation()

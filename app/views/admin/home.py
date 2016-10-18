"""Copyright 2015 Rafal Kowalski"""
import logging
import os
import urllib
from urllib2 import urlopen

from flask import url_for, redirect, request, session, flash
from flask.ext import login
from flask_admin import expose
from flask_admin.base import AdminIndexView
from flask.ext.scrypt import generate_password_hash

from app.helpers.flask_helpers import get_real_ip, slugify
from app.views.public.explore import erase_from_dict
from ...helpers.data import DataManager, save_to_db, get_google_auth, get_facebook_auth, create_user_password, \
    user_logged_in, record_activity
from ...helpers.data_getter import DataGetter
from ...helpers.helpers import send_email_with_reset_password_hash, send_email_confirmation, \
    get_serializer, get_request_stats
from app.helpers.oauth import OAuth, FbOAuth
from app.models.user import User
import geoip2.database
from flask import abort
from werkzeug.datastructures import ImmutableMultiDict


def intended_url():
    return request.args.get('next') or url_for('.index')


def record_user_login_logout(template, user):
    req_stats = get_request_stats()
    record_activity(
        template,
        user=user,
        **req_stats
    )


class MyHomeView(AdminIndexView):
    @expose('/')
    def index(self):
        call_for_speakers_events = DataGetter.get_call_for_speakers_events()
        upcoming_events = DataGetter.get_all_published_events().limit(12).all()
        placeholder_images = DataGetter.get_event_default_images()
        custom_placeholder = DataGetter.get_custom_placeholders()
        im_config = DataGetter.get_image_configs()
        im_size = ''
        for config in im_config:
            if config.page == 'front':
                im_size = config.size
        return self.render('gentelella/index.html',
                           call_for_speakers_events=call_for_speakers_events,
                           upcoming_events=upcoming_events,
                           placeholder_images=placeholder_images,
                           custom_placeholder=custom_placeholder,
                           im_size=im_size)

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        if request.method == 'GET':
            google = get_google_auth()
            auth_url, state = google.authorization_url(OAuth.get_auth_uri(), access_type='offline')
            session['oauth_state'] = state

            # Add Facebook Oauth 2.0 login
            facebook = get_facebook_auth()
            fb_auth_url, state = facebook.authorization_url(FbOAuth.get_auth_uri(), access_type='offline')
            session['fb_oauth_state'] = state
            return self.render('/gentelella/admin/login/login.html', auth_url=auth_url, fb_auth_url=fb_auth_url)
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

    @expose('/register/', methods=('GET', 'POST'))
    def register_view(self):
        """Register view page"""
        if request.method == 'GET':
            return self.render('/gentelella/admin/login/register.html')
        if request.method == 'POST':
            logging.info("Registration under process")
            s = get_serializer()
            data = [request.form['email'], request.form['password']]
            user = DataManager.create_user(data)
            form_hash = s.dumps(data)
            link = url_for('.create_account_after_confirmation_view', hash=form_hash, _external=True)
            send_email_confirmation(request.form, link)
            login.login_user(user)
            record_user_login_logout('user_login', user)
            logging.info('logged successfully')
            user_logged_in(user)
            return redirect(intended_url())

    @expose('/account/create/<hash>', methods=('GET',))
    def create_account_after_confirmation_view(self, hash):
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

    @expose('/password/new/<email>', methods=('GET', 'POST'))
    def create_password_after_oauth_login(self, email):
        s = get_serializer()
        email = s.loads(email)
        user = DataGetter.get_user_by_email(email)
        if request.method == 'GET':
            return self.render('/gentelella/admin/login/create_password.html')
        if request.method == 'POST':
            user = create_user_password(request.form, user)
            if user is not None:
                login.login_user(user)
                record_user_login_logout('user_login', user)
                user_logged_in(user)
                return redirect(intended_url())

    @expose('/password/reset', methods=('GET', 'POST'))
    def password_reset_view(self):
        """Password reset view"""
        if request.method == 'GET':
            return self.render('/gentelella/admin/login/password_reminder.html')
        if request.method == 'POST':
            email = request.form['email']
            user = DataGetter.get_user_by_email(email)
            if user:
                link = request.host + url_for(".change_password_view", hash=user.reset_password)
                send_email_with_reset_password_hash(email, link)
                flash('Please go to the link sent to your email to reset your password')
            return redirect(url_for('.login_view'))

    @expose('/reset_password/<hash>', methods=('GET', 'POST'))
    def change_password_view(self, hash):
        """Change password view"""
        if request.method == 'GET':
            return self.render('/gentelella/admin/login/change_password.html')
        if request.method == 'POST':
            DataManager.reset_password(request.form, hash)
            return redirect(url_for('.index'))

    @expose('/logout/')
    def logout_view(self):
        """Logout method which redirect to index"""
        record_user_login_logout('user_logout', login.current_user)
        login.logout_user()
        return redirect(url_for('.index'))

    @expose('/set_role', methods=('GET', 'POST'))
    def set_role(self):
        """Set user role method"""
        id = request.args['id']
        role = request.args['roles']
        user = DataGetter.get_user(id)
        user.role = role
        save_to_db(user, "User Role updated")
        return redirect(url_for('.roles_manager'))

    @expose('/manage_roles')
    def roles_manager(self):
        """Roles manager view"""
        users = DataGetter.get_all_users()
        events = DataGetter.get_all_events()
        return self.render('admin/role_manager.html',
                           users=users,
                           events=events)

    @expose('/sessions/', methods=('GET',))
    def view_user_sessions(self):
        sessions = DataGetter.get_user_sessions()
        return self.render('/gentelella/admin/session/user_sessions.html',
                           sessions=sessions)

    @expose('/forbidden/', methods=('GET',))
    def forbidden_view(self):
        return self.render('/gentelella/admin/forbidden.html')

    @expose('/browse/', methods=('GET',))
    def browse_view(self):
        params = request.args.items()
        params = dict((k, v) for k, v in params if v)

        def test_and_remove(key):
            if request.args.get(key):
                if request.args.get(key).lower() == request.args.get("query").lower():
                    erase_from_dict(params, 'query')

        if not request.args.get("location"):
            try:
                reader = geoip2.database.Reader(os.path.realpath('.') + '/static/data/GeoLite2-Country.mmdb')
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

        return redirect(url_for('explore.explore_view', location=slugify(country)) + '?' +
                        urllib.urlencode(params))

    @expose('/check_email/', methods=('POST', 'GET'))
    def check_duplicate_email(self):
        if request.method == 'GET':
            email = request.args['email']
            user = DataGetter.get_user_by_email(email, no_flash=True)
            if user is None:
                return '200 OK'
            else:
                return abort(404)

    @expose('/resend_email/')
    def resend_email_confirmation(self):
        user = DataGetter.get_user(login.current_user.id)
        s = get_serializer()
        data = [user.email, user.password]
        form_hash = s.dumps(data)
        link = url_for('.create_account_after_confirmation_view', hash=form_hash, _external=True)
        form = {"email": user.email, "password": user.password}
        form = ImmutableMultiDict(form)
        send_email_confirmation(form, link)
        return redirect(url_for('events.index_view'))

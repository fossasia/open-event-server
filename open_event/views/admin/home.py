"""Copyright 2015 Rafal Kowalski"""
import logging

from flask import url_for, redirect, request, session
from flask.ext import login
from flask_admin import expose
from flask_admin.base import AdminIndexView
from flask.ext.scrypt import generate_password_hash

from ...helpers.data import DataManager, save_to_db,get_google_auth,get_facebook_auth
from ...helpers.data_getter import DataGetter
from ...helpers.helpers import send_email_after_account_create, send_email_with_reset_password_hash
from open_event.helpers.oauth import OAuth, FbOAuth
from flask import current_app

def intended_url():
    return request.args.get('next') or url_for('.index')


class MyHomeView(AdminIndexView):

    @expose('/')
    def index(self):
        return self.render('gentelella/admin/login/admin.html')

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
                return redirect(url_for('admin.login_view'))

            _jwt = current_app.extensions['jwt']
            identity = _jwt.authentication_callback(email, request.form['password'])
            access_token = _jwt.jwt_encode_callback(identity)
            
            login.login_user(user)
            logging.info('logged successfully')
            redirect_to_intended = redirect(intended_url())
            response = current_app.make_response(redirect_to_intended)
            response.set_cookie('access_token', value=access_token)
            return response

    @expose('/register/', methods=('GET', 'POST'))
    def register_view(self):
        """Register view page"""
        if request.method == 'GET':
            return self.render('/gentelella/admin/login/register.html')
        if request.method == 'POST':
            logging.info("Registration under process")
            user = DataManager.create_user(request.form)
            login.login_user(user)
            send_email_after_account_create(request.form)
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
                return redirect(intended_url())

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

    @expose('/sessions/', methods=('GET', ))
    def view_user_sessions(self):
        sessions = DataGetter.get_user_sessions()
        return self.render('/gentelella/admin/session/user_sessions.html',
                           sessions=sessions)


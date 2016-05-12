"""Copyright 2015 Rafal Kowalski"""
import logging
import json
from flask import url_for, redirect, request,session
from flask.ext import login
from flask_admin import helpers, expose
from flask_admin.base import AdminIndexView

from ...forms.admin.auth.change_password import ChangePasswordForm
from ...forms.admin.auth.login_form import LoginForm
from ...forms.admin.auth.password_reminder_form import PasswordReminderForm
from ...forms.admin.auth.registration_form import RegistrationForm
from ...helpers.data import DataManager, save_to_db,get_google_auth,get_facebook_auth
from ...helpers.data_getter import DataGetter
from ...helpers.helpers import send_email_after_account_create, send_email_with_reset_password_hash
from open_event.helpers.oauth import OAuth,Fb_OAuth


def intended_url():
    return request.args.get('next') or url_for('.index')


class MyHomeView(AdminIndexView):
    @expose('/')
    def index(self):
        """Main page"""
        self._template = "admin/auth.html"
        if not login.current_user.is_authenticated:
            # print "Unauthenticated user"
            return redirect(url_for('.login_view'))
        else:
            # print "Authenticated user"
            self._template_args['events'] = DataGetter.get_all_events()
            self._template_args['owner_events'] = DataGetter.get_all_owner_events()
            return super(MyHomeView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        """Login view page"""
        # handle user login
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            login.login_user(user)

        if login.current_user.is_authenticated:
            return redirect(intended_url())
        
        #Add Google Oauth 2.0 Login
        google=get_google_auth()
        auth_url,state=google.authorization_url(OAuth.AUTH_URI,access_type='offline')
        session['oauth_state']=state
    
        facebook=get_facebook_auth()
        fb_auth_url, state = facebook.authorization_url(Fb_OAuth.AUTH_URI,access_type='offline')
        session['fb_oauth_state']=state

        link = '<p>Don\'t have an account? <a href="' + url_for('.register_view') + '">Click here to register.</a></p>' \
                                                                                    '<p><a href="' + url_for(
                '.password_reminder_view') + '">Forgot your password</a>?</p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
        self._template_args['auth_url'] = auth_url
        self._template_args['fb_auth_url'] = fb_auth_url
        self._template_args['events'] = DataGetter.get_all_events()
        self._template = "admin/auth.html"
        return super(MyHomeView, self).index()

    @expose('/register/', methods=('GET', 'POST'))
    def register_view(self):
        """Register view page"""
        form = RegistrationForm(request.form)
        if helpers.validate_form_on_submit(form):
            logging.info("Registration under process")
            user = DataManager.create_user(form)
            login.login_user(user)
            send_email_after_account_create(form)
            return redirect(intended_url())
        link = '<p>Already have an account? <a href="' + url_for('.login_view') + '">Click here to log in.</a></p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
        self._template_args['events'] = DataGetter.get_all_events()
        self._template = "admin/auth.html"
        return super(MyHomeView, self).index()

    @expose('/password/reminder', methods=('GET', 'POST'))
    def password_reminder_view(self):
        """Password reminder view"""
        form = PasswordReminderForm(request.form)
        if request.method == 'POST':
            if form.validate():
                email = form.email.data
                user = DataGetter.get_user_by_email(email)
                if user:
                    link = request.host + url_for(".change_password_view", hash=user.reset_password)
                    send_email_with_reset_password_hash(email, link)
                return redirect(intended_url())
        self._template_args['form'] = form
        self._template = "admin/auth.html"
        return super(MyHomeView, self).index()

    @expose('/reset_password/<hash>', methods=('GET', 'POST'))
    def change_password_view(self, hash):
        """Change password view"""
        form = ChangePasswordForm(request.form)
        if request.method == 'POST':
            if helpers.validate_form_on_submit(form):
                DataManager.update_user(form, hash)
                return redirect(url_for('.index'))
        self._template_args['name'] = 'Change Password'
        self._template_args['form'] = form
        self._template = "admin/auth.html"
        return super(MyHomeView, self).index()

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

   

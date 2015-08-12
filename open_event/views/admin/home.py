"""Copyright 2015 Rafal Kowalski"""
from flask import url_for, redirect, request
from flask.ext import login
from flask_admin.base import AdminIndexView
from flask_admin import helpers, expose

from ...forms.admin.auth.registration_form import RegistrationForm
from ...forms.admin.auth.login_form import LoginForm
from ...forms.admin.auth.change_password import ChangePasswordForm
from ...forms.admin.auth.password_reminder_form import PasswordReminderForm
from ...helpers.data import DataManager, save_to_db
from ...helpers.data_getter import DataGetter
from ...helpers.helpers import send_email_after_account_create, send_email_with_reset_password_hash

class MyHomeView(AdminIndexView):
    @expose('/')
    def index(self):
        self._template = "admin/auth.html"
        if not login.current_user.is_authenticated():
            return redirect(url_for('.login_view'))
        self._template_args['events'] = DataGetter.get_all_events()
        self._template_args['owner_events'] = DataGetter.get_all_owner_events(login.current_user.id)
        return super(MyHomeView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        # handle user login
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            login.login_user(user)

        if login.current_user.is_authenticated():
            return redirect(url_for('.index'))
        link = '<p>Don\'t have an account? <a href="' + url_for('.register_view') + '">Click here to register.</a></p>' \
                                                                                    '<p><a href="'+ url_for('.password_reminder_view') +'">Forgot your password</a>?</p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
        self._template_args['events'] = DataGetter.get_all_events()
        self._template = "admin/auth.html"
        return super(MyHomeView, self).index()

    @expose('/register/', methods=('GET', 'POST'))
    def register_view(self):
        form = RegistrationForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = DataManager.create_user(form)
            login.login_user(user)
            send_email_after_account_create(form)
            return redirect(url_for('.index'))
        link = '<p>Already have an account? <a href="' + url_for('.login_view') + '">Click here to log in.</a></p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
        self._template_args['events'] = DataGetter.get_all_events()
        self._template = "admin/auth.html"
        return super(MyHomeView, self).index()

    @expose('/password/reminder', methods=('GET', 'POST'))
    def password_reminder_view(self):

        form = PasswordReminderForm(request.form)
        if request.method == 'POST':
            if form.validate():
                email = form.email.data
                user = DataGetter.get_user_by_email(email)
                link = request.host + url_for(".change_password_view", hash=user.reset_password)
                send_email_with_reset_password_hash(email, link)
                return redirect(url_for('.index'))
        self._template_args['form'] = form
        self._template = "admin/auth.html"
        return super(MyHomeView, self).index()

    @expose('/reset_password/<hash>', methods=('GET', 'POST'))
    def change_password_view(self, hash):

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
        login.logout_user()
        return redirect(url_for('.index'))

    @expose('/set_role', methods=('GET', 'POST'))
    def set_role(self):
        id = request.args['id']
        role = request.args['roles']
        user = DataGetter.get_user(id)
        user.role = role
        save_to_db(user, "User Role updated")
        return redirect(url_for('.roles_manager'))

    @expose('/manage_roles')
    def roles_manager(self):
        users = DataGetter.get_all_users()
        events = DataGetter.get_all_events()
        return self.render('admin/role_manager.html',
                           users=users,
                           events=events)

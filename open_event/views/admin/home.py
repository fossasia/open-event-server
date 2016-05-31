"""Copyright 2015 Rafal Kowalski"""
import logging

from flask import url_for, redirect, request
from flask.ext import login
from flask_admin import helpers, expose
from flask_admin.base import AdminIndexView
from flask.ext.scrypt import generate_password_hash

from ...forms.admin.auth.change_password import ChangePasswordForm
from ...forms.admin.auth.password_reminder_form import PasswordReminderForm
from ...helpers.data import DataManager, save_to_db
from ...helpers.data_getter import DataGetter
from ...helpers.helpers import send_email_after_account_create, send_email_with_reset_password_hash
from open_event.models.user import User


def intended_url():
    return request.args.get('next') or url_for('.index')


class MyHomeView(AdminIndexView):

    @expose('/')
    def index(self):
        return self.render('gentelella/admin/login/admin.html')

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        if request.method == 'GET':
            return self.render('/gentelella/admin/login/login.html')
        if request.method == 'POST':
            username = request.form['username']
            users = User.query.filter_by(login=username)
            for user in users:
                if user.password == generate_password_hash(request.form['password'], user.salt):
                    valid_user = user
                    break
                else:
                    valid_user = None
            if valid_user is None:
                logging.info('No such user')
                return redirect(url_for('admin.login_view'))
            login.login_user(valid_user)
            logging.info('logged successfully')
            return redirect(intended_url())

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
                DataManager.reset_password(form, hash)
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

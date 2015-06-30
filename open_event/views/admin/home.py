"""Copyright 2015 Rafal Kowalski"""
from flask import url_for, redirect, request
from flask.ext import login
from flask.ext.admin.base import AdminIndexView
from flask.ext.admin import helpers, expose

from ...forms.admin.auth.registration_form import RegistrationForm
from ...forms.admin.auth.login_form import LoginForm
from open_event.models import db
from open_event.models.event import Event
from open_event.models.user import User
from ...helpers.data import DataManager

class MyHomeView(AdminIndexView):
    @expose('/')
    def index(self):
        self._template = "admin/auth.html"
        if not login.current_user.is_authenticated():
            return redirect(url_for('.login_view'))
        self._template_args['events'] = Event.query.all()
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
        link = '<p>Don\'t have an account? <a href="' + url_for('.register_view') + '">Click here to register.</a></p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
        self._template_args['events'] = Event.query.all()
        self._template = "admin/auth.html"
        return super(MyHomeView, self).index()

    @expose('/register/', methods=('GET', 'POST'))
    def register_view(self):
        form = RegistrationForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = DataManager.create_user(form)
            login.login_user(user)
            return redirect(url_for('.index'))
        link = '<p>Already have an account? <a href="' + url_for('.login_view') + '">Click here to log in.</a></p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
        self._template_args['events'] = Event.query.all()
        self._template = "admin/auth.html"
        return super(MyHomeView, self).index()

    @expose('/logout/')
    def logout_view(self):
        login.logout_user()
        return redirect(url_for('.index'))

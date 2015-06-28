"""Copyright 2015 Rafal Kowalski"""
from flask import url_for, redirect, request
from flask.ext import login
from flask.ext.admin import Admin
from flask.ext.admin.base import AdminIndexView
from flask.ext.admin import helpers, expose

from open_event.models import db
from open_event.models.event import Event
from open_event.models.user import User
from open_event.views.admin.models_views.event import EventView
from open_event.views.admin.models_views.api import ApiView
from ...forms.admin.auth.registration_form import RegistrationForm
from ...forms.admin.auth.login_form import LoginForm
from werkzeug.security import generate_password_hash, check_password_hash

class MyHomeView(AdminIndexView):
    @expose('/')
    def index(self):
        print dir(self._template_args)
        print dir(self)
        events = Event.query.all()
        self._template = "admin/auth.html"
        # return self.render('admin/base1.html', events=events)
        if not login.current_user.is_authenticated():
            return redirect(url_for('.login_view'))
        self._template_args['events'] = Event.query.all()
        return super(MyHomeView, self).index()
        # return self.render('/admin/auth.html', events=events)

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
        return super(MyHomeView, self).index()

    @expose('/register/', methods=('GET', 'POST'))
    def register_view(self):
        form = RegistrationForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = User()

            form.populate_obj(user)
            # we hash the users password to avoid saving it as plaintext in the db,
            # remove to use plain text:
            user.password = generate_password_hash(form.password.data)

            db.session.add(user)
            db.session.commit()

            login.login_user(user)
            return redirect(url_for('.index'))
        link = '<p>Already have an account? <a href="' + url_for('.login_view') + '">Click here to log in.</a></p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
        return super(MyHomeView, self).index()

    @expose('/logout/')
    def logout_view(self):
        login.logout_user()
        return redirect(url_for('.index'))



class AdminView(object):

    def __init__(self, app, app_name):
        self.app = app
        self.init_login()
        self.admin = Admin(name=app_name, template_mode='bootstrap3', index_view=MyHomeView())

    def init(self):
        self.admin.init_app(self.app)
        self._add_views()

    def _add_views(self):
        self._add_models_to_menu()

    def _add_models_to_menu(self):
        self.admin.add_view(EventView(Event, db.session))
        self.admin.add_view(ApiView(name='Api'))

    def init_login(self):
        login_manager = login.LoginManager()
        login_manager.init_app(self.app)

        # Create user loader function
        @login_manager.user_loader
        def load_user(user_id):
            return db.session.query(User).get(user_id)

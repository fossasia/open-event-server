import flask_login as login
from flask import url_for, redirect, render_template, current_app as app, Blueprint, request
from flask_scrypt import generate_password_hash
from wtforms import form, fields, validators
from flask_admin import Admin, BaseView, AdminIndexView, expose, helpers as admin_helpers
from flask_admin.contrib.sqla import ModelView
from app.models import db
from app.models.user import User


class AdminModelView(ModelView):
    def is_accessible(self):
        return login.current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('admin.index', next=request.url))


class LoginForm(form.Form):
    login = fields.TextField(validators=[validators.required()])
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        """
        validate login
        :param field:
        :return:
        """
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('Invalid user')

        if user.password != generate_password_hash(self.password.data, user.salt):
            raise validators.ValidationError('Invalid password')

        if not user.is_admin or not user.is_super_admin:
            raise validators.ValidationError('Access Forbidden. Admin Rights Required')

    def get_user(self):
        return User.query.filter_by(email=self.login.data).first()


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        """
        /admin
        :return:
        """
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))
        return super(MyAdminIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        """
        login view for flask-admin
        :return:
        """
        # handle user login
        form = LoginForm(request.form)
        if admin_helpers.validate_form_on_submit(form):
            user = form.get_user()
            login.login_user(user)

        if login.current_user.is_authenticated:
            return redirect(url_for('.index'))
        self._template_args['form'] = form
        return super(MyAdminIndexView, self).index()

    @expose('/logout/')
    def logout_view(self):
        login.logout_user()
        return redirect(url_for('.index'))


home_routes = Blueprint('home', __name__)


# Flask views
@home_routes.route('/')
def index():
    """
    Index route
    :return:
    """
    return render_template('index.html')


class BlueprintsManager:
    def __init__(self):
        pass

    @staticmethod
    def register(app):
        """
        Register blueprints
        :param app: a flask app instance
        :return:
        """
        app.register_blueprint(home_routes)
        admin = Admin(app, name='admin', template_mode='bootstrap3', index_view=MyAdminIndexView(),
                      base_template='my_master.html')

        # Get all the models in the db, all models should have a explicit __tablename__
        classes, models, table_names = [], [], []
        for clazz in db.Model._decl_class_registry.values():
            try:
                table_names.append(clazz.__tablename__)
                classes.append(clazz)
            except:
                pass
        for table in db.metadata.tables.items():
            if table[0] in table_names:
                models.append(classes[table_names.index(table[0])])

        for model in models:
            admin.add_view(AdminModelView(model, db.session))

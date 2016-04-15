"""Copyright 2015 Rafal Kowalski"""
from wtforms import form, StringField, PasswordField, validators
from flask.ext.scrypt import check_password_hash
from ....models import db
from ....models.user import User
from sqlalchemy import or_


class LoginForm(form.Form):
    """Login Form class"""
    login = StringField(u'Username or Email', validators=[validators.required()])
    password = PasswordField(validators=[validators.required()])

    def __init__(self, form):
        """Init class"""
        super(LoginForm, self).__init__(form)
        self.user = None

    def validate_login(self, field):
        """Login validation"""
        users = self.get_users()

        if users is None:
            raise validators.ValidationError('Invalid user')

        userFound = False
        for u in users:
            if check_password_hash(self.password.data.encode("utf-8"), u.password.encode('utf-8'), u.salt):
                userFound = True
                break
        if not userFound:
            raise validators.ValidationError('Invalid password')
        else:
            self.user = u

    def get_users(self):
        """Returns users by login/email"""
        return db.session.query(User).filter(or_(User.login==self.login.data, User.email==self.login.data))

    def get_user(self):
        """Get authenticated user"""
        return self.user

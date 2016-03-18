"""Copyright 2015 Rafal Kowalski"""
from wtforms import form, StringField, PasswordField, validators
from flask.ext.scrypt import check_password_hash
from ....models import db
from ....models.user import User


class LoginForm(form.Form):
    """Login Form class"""
    login = StringField(validators=[validators.required()])
    password = PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        """Login validation"""
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('Invalid user')

        if not check_password_hash(self.password.data.encode("utf-8"), user.password.encode('utf-8'), user.salt):
            raise validators.ValidationError('Invalid password')

    def get_user(self):
        """Returns user by login"""
        return db.session.query(User).filter_by(login=self.login.data).first()

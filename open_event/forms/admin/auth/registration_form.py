"""Copyright 2015 Rafal Kowalski"""
from wtforms import form, StringField, PasswordField, validators
from ....models import db
from ....models.user import User


class RegistrationForm(form.Form):
    login = StringField(u'Username', validators=[validators.required()])
    email = StringField(validators=[validators.email()])
    password = PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        if db.session.query(User).filter_by(login=self.login.data).count() > 0:
            raise validators.ValidationError('Duplicate username')

    def validate_email(self, field):
        if db.session.query(User).filter_by(email=self.email.data).count() > 0:
            raise validators.ValidationError('Duplicate email')

from wtforms import form, StringField, PasswordField, validators
from ....models import db
from ....models.user import User


class RegistrationForm(form.Form):
    login = StringField(validators=[validators.required()])
    email = StringField(validators=[validators.email()])
    password = PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        if db.session.query(User).filter_by(login=self.login.data).count() > 0:
            raise validators.ValidationError('Duplicate username')
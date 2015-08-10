"""Copyright 2015 Rafal Kowalski"""
from wtforms import form, PasswordField, validators

class ChangePasswordForm(form.Form):
    password = PasswordField(validators=[validators.required(), validators.length(min=8)])
    aprove_password = PasswordField(validators=[validators.required(), validators.length(min=8)])

    def validate_password(self, field):
        if self.password.data != self.aprove_password.data:
            raise validators.ValidationError('Passwords are different')

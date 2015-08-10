"""Copyright 2015 Rafal Kowalski"""
from wtforms import form, StringField, validators

class PasswordReminderForm(form.Form):
    email = StringField(validators=[validators.required(), validators.email()])


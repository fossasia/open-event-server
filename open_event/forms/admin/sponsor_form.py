"""Copyright 2015 Rafal Kowalski"""
from flask_wtf import Form
from wtforms import StringField, validators


class SponsorForm(Form):
    name = StringField('Name', [validators.DataRequired()])
    url = StringField('Url')
    logo = StringField('Logo')

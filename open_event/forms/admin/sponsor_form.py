"""Copyright 2015 Rafal Kowalski"""
from flask_wtf import Form
from wtforms import StringField, validators


class SponsorForm(Form):
    """Sponsor Form class"""
    name = StringField('Name', [validators.DataRequired()])
    url = StringField('Url', [validators.Optional(), validators.URL()])
    logo = StringField('Logo Url', [validators.Optional(), validators.URL()])

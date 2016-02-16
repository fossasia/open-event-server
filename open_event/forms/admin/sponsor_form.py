"""Copyright 2015 Rafal Kowalski"""
from flask_wtf import Form
from wtforms import StringField, validators
from flask_wtf.file import FileField

class SponsorForm(Form):
    """Sponsor Form class"""
    name = StringField('Name', [validators.DataRequired()])
    url = StringField('Url')
    logo = StringField('Logo Url')

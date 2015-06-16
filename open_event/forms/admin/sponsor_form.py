"""Copyright 2015 Rafal Kowalski"""
from flask_wtf import Form
from wtforms import StringField


class SponsorForm(Form):
    name = StringField('Name')
    url = StringField('Url')
    logo = StringField('Logo')

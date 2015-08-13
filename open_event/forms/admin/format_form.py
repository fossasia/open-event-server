"""Copyright 2015 Rafal Kowalski"""
from flask_wtf import Form
from wtforms import StringField, validators


class FormatForm(Form):
    """Level Form class"""
    name = StringField('Name', [validators.DataRequired()])
    label_en = StringField('Label En')

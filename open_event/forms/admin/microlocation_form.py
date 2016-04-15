"""Copyright 2015 Rafal Kowalski"""
from flask_wtf import Form
from wtforms import StringField, FloatField, validators, IntegerField


class MicrolocationForm(Form):
    """Microlocation form class"""
    name = StringField('Name', [validators.DataRequired()])
    latitude = FloatField('Latitude',[validators.optional()])
    longitude = FloatField('Longitude', [validators.optional()])
    floor = IntegerField('Floor', [validators.optional()])
    room = StringField('Room', [validators.optional()])

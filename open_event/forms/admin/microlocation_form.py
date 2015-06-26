"""Copyright 2015 Rafal Kowalski"""
from flask_wtf import Form
from wtforms import StringField, FloatField, validators, IntegerField
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from open_event.models.session import Session
from ...helpers.helpers import get_event_id


def get_sessions():
    return Session.query.filter_by(event_id=get_event_id())


class MicrolocationForm(Form):
    name = StringField('Name', [validators.DataRequired()])
    latitude = FloatField('Latitude', [validators.DataRequired()])
    longitude = FloatField('Longitude', [validators.DataRequired()])
    floor = IntegerField('Floor', [validators.optional()])
    session = QuerySelectField(query_factory=get_sessions, allow_blank=True)

"""Copyright 2015 Rafal Kowalski"""
from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import Length
from open_event.models.session import Session
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from ...helpers.helpers import get_event_id


def get_sessions():
    return Session.query.filter_by(event_id=get_event_id())


class TrackForm(Form):
    name = StringField('Name', [Length(min=6, max=35)])
    description = StringField('Description', [Length(min=4, max=300)])
    session = QuerySelectField(query_factory=get_sessions, allow_blank=True)

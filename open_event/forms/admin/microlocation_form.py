from flask_wtf import Form
from wtforms import StringField, FloatField, TextAreaField
from open_event.models.session import Session
from wtforms.ext.sqlalchemy.fields import QuerySelectField

def get_sessions():
    return Session.query.all()


class MicrolocationForm(Form):
    name = StringField('Name')
    latitude = FloatField('Latitude')
    longitude = FloatField('Longitude')
    floor = StringField('Floor')
    session = QuerySelectField(query_factory=get_sessions, allow_blank=True)
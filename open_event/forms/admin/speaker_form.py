from flask_wtf import Form
from wtforms import StringField, DateTimeField, TextAreaField
from open_event.models.session import Session
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField

def get_sessions():
    return Session.query.all()

class SpeakerForm(Form):
    name = StringField('Name')
    photo = StringField('Photo')
    biography = TextAreaField('Biography')
    email = StringField('Email')
    web = StringField('Web')
    twitter = StringField('Twitter')
    facebook = StringField('Facebook')
    github = StringField('Github')
    linkedin = StringField('Linkedin')
    organisation = StringField('Organisation')
    position = StringField('Position')
    country = StringField('Country')
    sessions = QuerySelectMultipleField(query_factory=get_sessions, allow_blank=True)
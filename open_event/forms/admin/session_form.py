from flask_wtf import Form
from wtforms import StringField, DateTimeField, TextField, TextAreaField
from wtforms.validators import Length
from open_event.models.session import Session
from open_event.models.speaker import Speaker
from wtforms.ext.sqlalchemy.fields import QuerySelectField
def get_speakers(): # query the topics (a.k.a categories)
    return Speaker.query.all()

class SessionForm(Form):
    title = StringField('title')
    subtitle = StringField('Subtitle')
    abstract = TextAreaField('Abstract')
    description = TextAreaField('Description')
    start_time = DateTimeField('Start Time')
    end_time = DateTimeField('End Time')
    type = StringField('Type')
    level = StringField('Level')
    speakers = QuerySelectField(query_factory=get_speakers, allow_blank=True)
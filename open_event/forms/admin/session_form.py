from flask_wtf import Form
from wtforms import StringField, DateTimeField, TextField, TextAreaField
from wtforms.validators import Length
from open_event.models.session import Session

class SessionForm(Form):
    class Meta:
        model = Session
    title = StringField('title', [Length(min=6, max=35)])
    subtitle = StringField('Subtitle', [Length(min=4, max=25)])
    abstract = TextAreaField('Abstract')
    description = TextAreaField('Description')
    start_time = DateTimeField('Start Time')
    end_time = DateTimeField('End Time')
    type = StringField('Type')
    level = StringField('Level')

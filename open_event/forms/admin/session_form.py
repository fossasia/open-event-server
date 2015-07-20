"""Copyright 2015 Rafal Kowalski"""
from flask_wtf import Form
from flask import flash
from wtforms import StringField, TextAreaField, validators
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField
from flask.ext.admin.form.fields import DateTimeField

from open_event.models.speaker import Speaker
from ...helpers.helpers import get_event_id
from ...helpers.data_getter import DataGetter

def get_speakers():
    return Speaker.query.filter_by(event_id=get_event_id())


class SessionForm(Form):
    title = StringField('Title', [validators.DataRequired()])
    subtitle = StringField('Subtitle')
    abstract = TextAreaField('Abstract')
    description = TextAreaField('Description', [validators.DataRequired()])
    start_time = DateTimeField('Start Time', [validators.DataRequired()])
    end_time = DateTimeField('End Time', [validators.DataRequired()])
    type = StringField('Type')
    level = StringField('Level')
    speakers = QuerySelectMultipleField(query_factory=get_speakers, allow_blank=True)

    def validate_date(self):
        event = DataGetter.get_event(get_event_id())
        session_start = self.start_time.data
        session_end = self.end_time.data
        if not (event.start_time <= session_start and session_end <= event.end_time and session_start < session_end):
            flash("Date incorrect")
            return False
        return True
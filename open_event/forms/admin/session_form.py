"""Copyright 2015 Rafal Kowalski"""
from flask_wtf import Form
from wtforms import StringField, TextAreaField
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField, QuerySelectField
from wtforms.validators import DataRequired
from flask_admin.form.fields import DateTimeField

from open_event.models.speaker import Speaker
from ...helpers.helpers import get_event_id
from ...helpers.validators import CustomDateSessionValidate
from ...helpers.data_getter import DataGetter


def get_speakers():
    """Returns Event's speakers"""
    return Speaker.query.filter_by(event_id=get_event_id())


class SessionForm(Form):
    """Session Form class"""
    title = StringField('Title', [DataRequired()])
    subtitle = StringField('Subtitle')
    abstract = TextAreaField('Abstract')
    description = TextAreaField('Description', [DataRequired()])
    start_time = DateTimeField('Start Time', [DataRequired(), CustomDateSessionValidate()])
    end_time = DateTimeField('End Time', [DataRequired(), CustomDateSessionValidate()])
    level = QuerySelectField(label='Level', query_factory=DataGetter.get_levels, allow_blank=True)
    format = QuerySelectField(label='Format', query_factory=DataGetter.get_formats, allow_blank=True)
    language = QuerySelectField(label='Language', query_factory=DataGetter.get_languages, allow_blank=True)
    speakers = QuerySelectMultipleField(query_factory=get_speakers, allow_blank=True)
    microlocation = QuerySelectField(label='Microlocation', query_factory=DataGetter.get_microlocations_by_event_id,
                                     allow_blank=True)

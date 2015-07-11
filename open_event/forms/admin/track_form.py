"""Copyright 2015 Rafal Kowalski"""
from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import Length, DataRequired
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from ...helpers.data_getter import DataGetter


class TrackForm(Form):
    name = StringField('Name', [Length(min=6, max=35)])
    description = StringField('Description', [Length(min=4, max=300)])
    track_image_url = StringField('Image')
    session = QuerySelectField(query_factory=DataGetter.get_sessions_by_event_id, allow_blank=True)

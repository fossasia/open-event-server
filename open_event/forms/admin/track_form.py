"""Copyright 2015 Rafal Kowalski"""
from flask_wtf import Form
from flask_admin.form.widgets import Select2Widget
from wtforms import StringField
from wtforms.validators import Length
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField
from ...helpers.data_getter import DataGetter


class TrackForm(Form):
    """Track Form class"""
    name = StringField('Name', [Length(min=6, max=35)])
    description = StringField('Description', [Length(min=4, max=1000)])
    track_image_url = StringField('Image')
    sessions = QuerySelectMultipleField(
            query_factory=DataGetter.get_sessions_by_event_id,
            widget=Select2Widget(multiple=True)
    )

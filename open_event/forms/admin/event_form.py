"""Copyright 2015 Rafal Kowalski"""
from flask_wtf import Form
from wtforms import StringField, FloatField, SelectField
from wtforms.validators import DataRequired
from flask_admin.form.fields import DateTimeField
from ...helpers.validators import CustomDateEventValidate
from ...helpers.data_getter import DataGetter
from wtforms_components import ColorField
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField, QuerySelectField
from flask_wtf.file import FileField

class EventForm(Form):
    """Event Form class"""
    name = StringField('Name', [DataRequired()])
    latitude = FloatField('Latitude')
    longitude = FloatField('Longitude')
    location_name = StringField('Location name')
    color = ColorField('Color')
    start_time = DateTimeField('Start Time', [DataRequired(), CustomDateEventValidate()])
    end_time = DateTimeField('End Time', [DataRequired(), CustomDateEventValidate()])
    logo = FileField('Logo')
    # logo = QuerySelectField(query_factory=DataGetter.get_all_owner_files, allow_blank=True)
    email = StringField('Email')
    slogan = StringField('Slogan')
    url = StringField('Url')

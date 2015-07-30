"""Copyright 2015 Rafal Kowalski"""
from flask_wtf import Form
from wtforms import StringField, FloatField, SelectField
from wtforms.validators import DataRequired
from flask_admin.form.fields import DateTimeField
from ...helpers.validators import CustomDateEventValidate
from ...helpers.data_getter import DataGetter


class EventForm(Form):
    """Event Form class"""
    name = StringField('Name', [DataRequired()])
    latitude = FloatField('Latitude', [DataRequired()])
    longitude = FloatField('Longitude', [DataRequired()])
    location_name = StringField('Location name')
    color = StringField('Color')
    start_time = DateTimeField('Start Time', [DataRequired(), CustomDateEventValidate()])
    end_time = DateTimeField('End Time', [DataRequired(), CustomDateEventValidate()])
    logo = SelectField('Logo',coerce=str, choices=DataGetter.get_all_files_tuple())
    email = StringField('Email')
    slogan = StringField('Slogan')
    url = StringField('Url')

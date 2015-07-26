"""Copyright 2015 Rafal Kowalski"""
from flask_wtf import Form
from wtforms import StringField, FloatField, SelectField
from wtforms.validators import DataRequired
from flask.ext.admin.form.fields import DateTimeField
from ...helpers.validators import CustomDateEventValidate
from ...helpers.data_getter import DataGetter


class EventForm(Form):
    name = StringField('Name', [DataRequired()])
    latitude = FloatField('Latitude', [DataRequired()])
    longitude = FloatField('Longitude', [DataRequired()])
    location_name = StringField('Location name')
    color = StringField('Color')
    start_time = DateTimeField('Start Time', [DataRequired(), CustomDateEventValidate()])
    end_time = DateTimeField('End Time', [DataRequired(), CustomDateEventValidate()])
    logo = SelectField(choices=DataGetter.get_all_files())
    email = StringField('Email')
    slogan = StringField('Slogan')
    url = StringField('Url')

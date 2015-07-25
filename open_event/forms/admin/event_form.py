"""Copyright 2015 Rafal Kowalski"""
from flask_wtf import Form
from wtforms import StringField, FloatField, validators, FileField
from wtforms.validators import DataRequired
from flask.ext.admin.form.fields import DateTimeField
from ...helpers.validators import CustomDateEventValidate
from ...helpers.data_getter import DataGetter
from wtforms.ext.sqlalchemy.fields import QuerySelectField


class EventForm(Form):
    name = StringField('Name', [DataRequired()])
    latitude = FloatField('Latitude', [DataRequired()])
    longitude = FloatField('Longitude', [DataRequired()])
    location_name = StringField('Location name')
    color = StringField('Color')
    start_time = DateTimeField('Start Time', [DataRequired(), CustomDateEventValidate()])
    end_time = DateTimeField('End Time', [DataRequired(), CustomDateEventValidate()])
    logo = QuerySelectField(query_factory=DataGetter.get_all_files, allow_blank=True)
    email = StringField('Email')
    slogan = StringField('Slogan')
    url = StringField('Url')

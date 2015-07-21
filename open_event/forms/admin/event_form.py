"""Copyright 2015 Rafal Kowalski"""
from flask import flash
from flask_wtf import Form
from wtforms import StringField, FloatField, validators, IntegerField, FileField
from flask.ext.admin.form.fields import DateTimeField
from ...helpers.validators import CustomDateEventValidate

class EventForm(Form):
    name = StringField('Name', [validators.DataRequired()])
    latitude = FloatField('Latitude', [validators.DataRequired()])
    longitude = FloatField('Longitude', [validators.DataRequired()])
    location_name = StringField('Location name')
    color = StringField('Color')
    start_time = DateTimeField('Start Time', [validators.DataRequired(), CustomDateEventValidate()])
    end_time = DateTimeField('End Time', [validators.DataRequired(), CustomDateEventValidate()])
    logo = FileField('Logo')
    email = StringField('Email')
    slogan = StringField('Slogan')
    url = StringField('Url')


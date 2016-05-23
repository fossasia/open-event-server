"""Copyright 2015 Rafal Kowalski"""
from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import Length


class TrackForm(Form):
    """Track Form class"""
    name = StringField('Name', [Length(min=6, max=35)])
    description = StringField('Description', [Length(min=4, max=1000)])
    track_image_url = StringField('Image')

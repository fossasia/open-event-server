from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import Length
from open_event.models.track import Track

class TrackForm(Form):
    class Meta:
        model = Track
    name = StringField('Name', [Length(min=6, max=35)])
    description = StringField('Description', [Length(min=4, max=25)])
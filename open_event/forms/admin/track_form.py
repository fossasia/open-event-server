from flask_wtf import Form
from wtforms import StringField, SelectField
from wtforms.validators import Length
# from open_event.models.track import Track
from open_event.models.session import Session
from open_event import app



class TrackForm(Form):
    # class Meta:
    #     model = Track
    name = StringField('Name', [Length(min=6, max=35)])
    description = StringField('Description', [Length(min=4, max=25)])
    session = SelectField(choices=[(x.id, x.name) for x in Session.query.all()])

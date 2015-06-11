from flask_wtf import Form
from wtforms import StringField, SelectField
from wtforms.validators import Length
from open_event.models.session import Session


class TrackForm(Form):
    name = StringField('Name', [Length(min=6, max=35)])
    description = StringField('Description', [Length(min=4, max=25)])
    session = SelectField(choices=[(x.id, x.title) for x in Session.query.all()], coerce=int)

from flask_wtf import Form
from wtforms import StringField, FloatField, TextAreaField
from open_event.models.session import Session
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from flask_admin.form.fields import Select2Field
def get_sessions():
    return [(session.id, session.title) for session in Session.query.all()]


class MicrolocationForm(Form):
    name = StringField('Name')
    latitude = FloatField('Latitude')
    longitude = FloatField('Longitude')
    floor = StringField('Floor')
    # session = Select2Field(choices=get_sessions(), allow_blank=True, coerce=int)

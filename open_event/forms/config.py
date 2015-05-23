from flask.ext.wtf import Form
from wtforms import SubmitField, StringField
from wtforms_components import ColorField


class ConfigForm(Form):
    logo = StringField("Logo")
    email = StringField("Email")
    title = StringField("Title")
    color = ColorField("Color")
    submit = SubmitField("Send")

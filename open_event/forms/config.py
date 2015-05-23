from flask.ext.wtf import Form
from wtforms import SubmitField, StringField
from wtforms.validators import Required


class ConfigForm(Form):
  logo = StringField("logo")
  email = StringField("Email")
  title = StringField("Message")
  color = StringField("Send")
  submit = SubmitField("Send")

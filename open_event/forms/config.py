
from wtforms import Form, SubmitField, StringField, validators
from wtforms_components import ColorField


class ConfigForm(Form):
    logo = StringField("Logo")
    email = StringField("Email", [validators.required()])
    title = StringField("Title")
    color = ColorField("Color")
    submit = SubmitField("Update")

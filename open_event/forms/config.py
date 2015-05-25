
from wtforms import Form, SubmitField, StringField, validators
from wtforms_components import ColorField


class ConfigForm(Form):
    logo = StringField("Logo")
    email = StringField("Email", [validators.Email()])
    title = StringField("Title", [validators.required(), validators.Length(min=1, max=30)])
    color = ColorField("Color", [validators.required()])
    submit = SubmitField("Save")

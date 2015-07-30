from flask_wtf import Form
from wtforms import FileField


class FileForm(Form):
    """File Form class"""
    file = FileField('File')

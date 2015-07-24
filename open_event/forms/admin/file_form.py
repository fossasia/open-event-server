from flask_wtf import Form
from wtforms import FileField


class FileForm(Form):
    file = FileField('File')

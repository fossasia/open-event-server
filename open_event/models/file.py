"""Copyright 2015 Rafal Kowalski"""
from . import db


class File(db.Model):
    __tablename__ = 'files'
    id = db.Column(db.Integer,
                   primary_key=True)
    name = db.Column(db.String,
                     nullable=False)
    path = db.Column(db.String,
                         nullable=False)

    def __init__(self,
                 name=None,
                 path=None):
        self.name = name
        self.path = path

    def __repr__(self):
        return '<File %r>' % (self.name)

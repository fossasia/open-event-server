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
    owner_id = db.Column(db.Integer,
                         db.ForeignKey('user.id'))

    def __init__(self,
                 name=None,
                 path=None,
                 owner_id=None):
        self.name = name
        self.path = path
        self.owner_id = owner_id
    def __repr__(self):
        return '<File %r>' % (self.name)

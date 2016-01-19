"""Copyright 2015 Rafal Kowalski"""
from . import db


class File(db.Model):
    """File model class"""
    __tablename__ = 'files'
    id = db.Column(db.Integer,
                   primary_key=True)
    name = db.Column(db.String,
                     nullable=False)
    path = db.Column(db.String,
                         nullable=False)
    owner_id = db.Column(db.Integer,
                         db.ForeignKey('user.id'))
    is_image = db.Column(db.Boolean)

    def __init__(self,
                 name=None,
                 path=None,
                 owner_id=None,
                 is_image=None):
        self.name = name
        self.path = path
        self.owner_id = owner_id
        self.is_image = is_image
    def __repr__(self):
        return '<File %r>' % (self.name)

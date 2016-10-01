"""Copyright 2015 Rafal Kowalski"""
from . import db


class Role(db.Model):
    """Event Role
    """
    __tablename__ = 'role'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    title_name = db.Column(db.String)

    def __init__(self, name, title_name):
        self.name = name
        self.title_name = title_name

    def __repr__(self):
        return '<Role %r>' % self.name

    def __str__(self):
        return str(self).encode('utf-8')

    def __unicode__(self):
        return self.name

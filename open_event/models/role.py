"""Copyright 2015 Rafal Kowalski"""
from . import db

user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)


class Role(db.Model):
    __tablename__ = 'role'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    users = db.relationship("User", secondary=user_roles, back_populates="roles")

    def __init__(self, name=None):
        self.name = name

    def __repr__(self):
        return '<Role %r>' % self.name

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.name

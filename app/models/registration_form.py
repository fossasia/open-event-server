import json

from . import db


REGISTRATION_FORM = {
    "firstname": {"include": 1, "require": 1},
    "email": {"include": 1, "require": 1},
    "lastname": {"include": 1, "require": 1},

}



class Forms(db.Model):
    """custom form model class"""
    __tablename__ = 'custom_forms'
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String, nullable=False)
    lastname = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    events = db.relationship("Event", backref="custom_forms")

    def __init__(self, event_id=None, firstname=None, lastname=None):
        self.event_id = event_id
        self.firstname = firstname
        self.lastname = lastname

    def __repr__(self):
        return '<Form %r>' % self.id

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return 'CustomForm %r' % self.id

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""

        return {'id': self.id, 'registration_form': self.registration_form}

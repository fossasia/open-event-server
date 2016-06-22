from datetime import datetime

from . import db


ACTIVITIES = {
    'update_profile': 'Profile of user {} updated',
    'update_event': 'Event {} updated',
    'create_event': 'Event {} created',
    'create_role': 'Role {} created for {} in event {}'
}


class Activity(db.Model):
    __tablename__ = 'activity'
    id = db.Column(db.Integer, primary_key=True)
    actor = db.Column(db.String)  # user email + id
    time = db.Column(db.DateTime)
    namespace = db.Column(db.String)
    detail = db.Column(db.String)

    def __init__(self, actor=None, time=None, namespace=None, detail=None):
        self.actor = actor
        self.time = time
        if self.time is None:
            self.time = datetime.now()
        self.namespace = namespace
        self.detail = detail

    def __repr__(self):
        return '<Activity by %s>' % (self.actor)

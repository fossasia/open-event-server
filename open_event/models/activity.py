from datetime import datetime

from . import db


ACTIVITIES = {
    'create_user': 'User {user} created',
    'update_user': 'Profile of user {user} updated',
    'update_event': 'Event {event} updated',
    'create_event': 'Event {event} created',
    'delete_event': 'Event {event} deleted',
    'create_role': 'Role {role} created for {user} in event {event}',
    'update_role': 'Role update to {role} for {user} in event {event}',
    'create_session': 'Session {session} was created'
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

from datetime import datetime

from . import db


ACTIVITIES = {
    'create_user': 'User {user} created',
    'update_user': 'Profile of user {user} updated',
    'update_event': 'Event {event_id} updated',
    'create_event': 'Event {event_id} created',
    'delete_event': 'Event {event_id} deleted',
    'import_event': 'Event {event_id} imported',
    'publish_event': 'Event {event_id} {status}',
    'create_role': 'Role {role} created for user {user} in event {event_id}',
    'update_role': 'Role updated to {role} for user {user} in event {event_id}',
    'delete_role': 'User {user} removed from role {role} in event {event_id}',
    'create_session': 'Session {session} was created in event {event_id}',
    'invite_user': 'Invitation sent to user {user_id} for event {event_id}',
    'create_track': 'Track {track} was created in event {event_id}',
    'update_track': 'Track {track} of event {event_id} was updated',
    'remove_track': 'Track {track} of event {event_id} was deleted',
    'create_speaker': 'Speaker {speaker} was created in event {event_id}',
    'remove_speaker': 'Speaker {speaker} of event {event_id} was deleted',
    'update_speaker': 'Speaker {speaker} of event {event_id} was updated',
    'add_speaker_to_session': 'Speaker {speaker} added to session {session} of event {event_id}',
    'system_admin': 'User {user} {status} system admin',
    'update_user_email': 'User {user_id}\'s email changed from {old} to {new}'
}


class Activity(db.Model):
    __tablename__ = 'activity'
    id = db.Column(db.Integer, primary_key=True)
    actor = db.Column(db.String)  # user email + id
    time = db.Column(db.DateTime)
    action = db.Column(db.String)

    def __init__(self, actor=None, time=None, action=None):
        self.actor = actor
        self.time = time
        if self.time is None:
            self.time = datetime.now()
        self.action = action

    def __repr__(self):
        return '<Activity by %s>' % (self.actor)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return 'Activity by %r' % self.actor

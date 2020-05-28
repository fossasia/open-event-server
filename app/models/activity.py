from sqlalchemy.sql import func

from app.models import db

ACTIVITIES = {
    'create_user': 'User {user} created',
    'update_user': 'Profile of user {user} updated',
    'update_user_email': 'User {user_id} email changed from {old} to {new}',
    'user_login': 'User {user} login from IP {ip} using browser {browser} on {platform} platform',
    'user_logout': 'User {user} logout from IP {ip} using browser {browser} on {platform} platform',
    'update_event': 'Event {event_id} updated',
    'create_event': 'Event {event_id} created',
    'delete_event': 'Event {event_id} deleted',
    'import_event': 'Event {event_id} imported',
    'publish_event': 'Event {event_id} {status}',
    'export_event': 'Event {event_id} exported',
    'create_role': 'Role {role} created for user {user} in event {event_id}',
    'update_role': 'Role updated to {role} for user {user} in event {event_id}',
    'delete_role': 'User {user} removed from role {role} in event {event_id}',
    'create_session': 'Session {session} was created in event {event_id}',
    'update_session': 'Session {session} of event {event_id} updated',
    'delete_session': 'Session {session} of event {event_id} deleted',
    'create_track': 'Track {track} was created in event {event_id}',
    'update_track': 'Track {track} of event {event_id} updated',
    'delete_track': 'Track {track} of event {event_id} deleted',
    'create_speaker': 'Speaker {speaker} was created in event {event_id}',
    'delete_speaker': 'Speaker {speaker} of event {event_id} deleted',
    'update_speaker': 'Speaker {speaker} of event {event_id} updated',
    'add_speaker_to_session': 'Speaker {speaker} added to session {session} of event {event_id}',
    'invite_user': 'Invitation sent to user {user_id} for event {event_id}',
    'system_admin': 'User {user} {status} system admin',
    'mail_event': 'Mail sent to {email}, action: {action}, subject: {subject}',
    'notification_event': 'Notification sent to {user}, action: {action}, title: {title}',
}


class Activity(db.Model):
    __tablename__ = 'activities'
    id = db.Column(db.Integer, primary_key=True)
    actor = db.Column(db.String)  # user email + id
    time = db.Column(db.DateTime(timezone=True), default=func.now())
    action = db.Column(db.String)

    def __repr__(self):
        return '<Activity by %s>' % self.actor

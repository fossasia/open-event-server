"""Copyright 2015 Rafal Kowalski"""
from . import db


class EmailNotification(db.Model):
    """email notifications model class"""
    __tablename__ = 'email_notification'
    id = db.Column(db.Integer,
                   primary_key=True)
    next_event = db.Column(db.Integer)
    new_paper = db.Column(db.Integer)
    session_accept_reject = db.Column(db.Integer)
    session_schedule = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))

    def __init__(self,
                 next_event=0,
                 new_paper=0,
                 session_accept_reject=0,
                 session_schedule=0,
                 user_id=None,
                 event_id=None):
        self.next_event = next_event
        self.new_paper = new_paper
        self.session_accept_reject = session_accept_reject
        self.session_schedule = session_schedule
        self.user_id = user_id
        self.event_id = event_id

    def __str__(self):
        return 'User:' + unicode(self.user_id).encode('utf-8') + ' Event: ' + unicode(self.event_id).encode('utf-8')

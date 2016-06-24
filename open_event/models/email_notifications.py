"""Copyright 2015 Rafal Kowalski"""
from . import db


class EmailNotification(db.Model):
    """email notifications model class"""
    __tablename__ = 'email_notification'
    id = db.Column(db.Integer,
                   primary_key=True)
    next_event = db.Column(db.Binary)
    new_paper = db.Column(db.Binary)
    session_accept_reject = db.Column(db.Binary)
    session_schedule = db.Column(db.Binary)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))

    def __init__(self,
                 next_event=None,
                 new_paper=None,
                 session_accept_reject=None,
                 session_schedule=None):
        self.next_event = next_event
        self.new_paper = new_paper
        self.session_accept_reject = session_accept_reject
        self.session_schedule = session_schedule

    def __str__(self):
        return unicode(self).encode('utf-8')

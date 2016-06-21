from datetime import datetime

from . import db


USER_REGISTER = 'User Registration'
USER_CONFIRM = 'User Confirmation'
INVITE_PAPERS = 'Invitation For Papers'
NEW_SESSION = 'New Session Proposal'
PASSWORD_RESET = 'Reset Password'


class Mail(db.Model):
    __tablename__ = 'mails'
    id = db.Column(db.Integer, primary_key=True)
    recipient = db.Column(db.String)
    time = db.Column(db.DateTime)
    action = db.Column(db.String)
    subject = db.Column(db.String)
    message = db.Column(db.String)

    def __init__(self, recipient=None, time=None, action=None, subject=None,
                 message=None):
        self.recipient = recipient
        self.time = time
        if self.time is None:
            self.time = datetime.now()
        self.action = action
        self.subject = subject
        self.message = message

    def __repr__(self):
        return '<Mail %d to %s>' % (self.id, self.recipient)

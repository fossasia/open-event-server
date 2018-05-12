from app.models import db

USER_REGISTER = 'User Registration'
USER_CONFIRM = 'User Confirmation'
INVITE_PAPERS = 'Invitation For Papers'
NEXT_EVENT = 'Next Event'
NEW_SESSION = 'New Session Proposal'
PASSWORD_RESET = 'Reset Password'
EVENT_ROLE = 'Event Role Invitation'
SESSION_ACCEPT_REJECT = 'Session Accept or Reject'
SESSION_SCHEDULE = 'Session Schedule Change'
EVENT_PUBLISH = 'Event Published'
AFTER_EVENT = 'After Event'


class MessageSettings(db.Model):
    __tablename__ = 'message_settings'
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String)
    mail_status = db.Column(db.Integer)
    notification_status = db.Column(db.Integer)
    user_control_status = db.Column(db.Integer)

    def __init__(self, action=None, mail_status=None, notification_status=None, user_control_status=None):
        self.action = action
        self.mail_status = mail_status
        self.notification_status = notification_status
        self.user_control_status = user_control_status

    def __repr__(self):
        return '<Message Setting %r >' % self.action

    def __str__(self):
        return self.__repr__()

    @property
    def serialize(self):
        """Return object data in easily serializable format"""

        return {'id': self.id,
                'action': self.action,
                'mail_status': self.mail_status,
                'notification_status': self.notification_status,
                'user_control_status': self.user_control_status}

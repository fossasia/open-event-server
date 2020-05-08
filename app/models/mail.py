from sqlalchemy.sql import func

from app.models import db

USER_REGISTER = 'User Registration'
USER_CONFIRM = 'User Confirmation'
USER_CHANGE_EMAIL = "User email"
INVITE_PAPERS = 'Invitation For Papers'
NEXT_EVENT = 'Next Event'
NEW_SESSION = 'New Session Proposal'
PASSWORD_RESET = 'Reset Password'
PASSWORD_RESET_AND_VERIFY = 'Reset Password and Account Verification'
PASSWORD_CHANGE = 'Change Password'
EVENT_ROLE = 'Event Role Invitation'
USER_EVENT_ROLE = 'User Event Role Invitation'
SESSION_ACCEPT_REJECT = 'Session Accept or Reject'
SESSION_SCHEDULE = 'Session Schedule Change'
EVENT_PUBLISH = 'Event Published'
AFTER_EVENT = 'After Event'
USER_REGISTER_WITH_PASSWORD = 'User Registration during Payment'
TICKET_PURCHASED = 'Ticket(s) Purchased'
TICKET_PURCHASED_ATTENDEE = 'Ticket(s) purchased to Attendee    '
TICKET_PURCHASED_ORGANIZER = 'Ticket(s) Purchased to Organizer'
TICKET_CANCELLED = 'Ticket(s) cancelled'
EVENT_EXPORTED = 'Event Exported'
EVENT_EXPORT_FAIL = 'Event Export Failed'
MAIL_TO_EXPIRED_ORDERS = 'Mail Expired Orders'
MONTHLY_PAYMENT_EMAIL = 'Monthly Payment Email'
MONTHLY_PAYMENT_FOLLOWUP_EMAIL = 'Monthly Payment Follow Up Email'
EVENT_IMPORTED = 'Event Imported'
EVENT_IMPORT_FAIL = 'Event Import Failed'
TEST_MAIL = 'Test Mail'


class Mail(db.Model):
    __tablename__ = 'mails'
    id = db.Column(db.Integer, primary_key=True)
    recipient = db.Column(db.String)
    time = db.Column(db.DateTime(timezone=True), default=func.now())
    action = db.Column(db.String)
    subject = db.Column(db.String)
    message = db.Column(db.String)

    def __repr__(self):
        return '<Mail %r to %r>' % (self.id, self.recipient)

from app.models import Role, db, Mail

class EventMailing:
    def __init__(self, role, subject, message):
        self.role = role
        self.subject = subject
        self.message = message

    def save_emails(self):
        role_name = self.role
        subject = self.subject
        message = self.message
        role = Role.query.filter_by(name=role_name).first()
        recipients = [attendee.email for attendee in role.attendees]

        for recipient in recipients:
            mail = Mail(recipient=recipient, subject=subject, message=message, action="save")
            db.session.add(mail)
        
        db.session.commit()

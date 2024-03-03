from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField
from app.models import Role, db, Mail

class EventMailingForm(FlaskForm):
    role = SelectField('Role', choices=[(role.name, role.title_name) for role in Role.query.all()])
    subject = StringField('Subject')
    message = TextAreaField('Message')

    def save_emails(self):
        role_name = self.role.data
        subject = self.subject.data
        message = self.message.data
        role = Role.query.filter_by(name=role_name).first()
        recipients = [attendee.email for attendee in role.attendees]

        for recipient in recipients:
            mail = Mail(recipient=recipient, subject=subject, message=message, action="save")
            db.session.add(mail)
        
        db.session.commit()

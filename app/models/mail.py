from sqlalchemy.sql import func

from app.models import db


class Mail(db.Model):
    __tablename__ = 'mails'
    id = db.Column(db.Integer, primary_key=True)
    recipient = db.Column(db.String)
    time = db.Column(db.DateTime(timezone=True), default=func.now())
    action = db.Column(db.String)
    subject = db.Column(db.String)
    message = db.Column(db.String)

    def __repr__(self):
        return f'<Mail {self.id!r} to {self.recipient!r}>'

from sqlalchemy.orm import backref
from sqlalchemy.sql import func

from app.models import db


class ExportJob(db.Model):
    """Export Jobs model class"""

    __tablename__ = 'export_jobs'
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String, nullable=False)
    starts_at = db.Column(db.DateTime(timezone=True), default=func.now())

    user_email = db.Column(db.String)
    # not linking to User because when user is deleted, this will be lost

    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    event = db.relationship('Event', backref=backref('export_jobs'))

    def __repr__(self):
        return '<ExportJob %d for event %d>' % (self.id, self.event.id)

from __future__ import unicode_literals

from datetime import datetime

import pytz
from future.utils import python_2_unicode_compatible
from sqlalchemy.orm import backref

from app.models import db
from utils.compat import u


@python_2_unicode_compatible
class ExportJob(db.Model):
    """Export Jobs model class"""
    __tablename__ = 'export_jobs'
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String, nullable=False)
    starts_at = db.Column(db.DateTime(timezone=True))

    user_email = db.Column(db.String)
    # not linking to User because when user is deleted, this will be lost

    event_id = db.Column(
        db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    event = db.relationship('Event', backref=backref('export_jobs'))

    def __init__(self, task=None, user_email=None, event=None):
        self.task = task
        self.user_email = user_email
        self.event = event
        self.starts_at = datetime.now(pytz.utc)

    def __repr__(self):
        return '<ExportJob %d for event %d>' % (self.id, self.event.id)

    def __str__(self):
        return u(self.__repr__())

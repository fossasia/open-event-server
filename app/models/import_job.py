from datetime import datetime

import pytz

from app.models import db


class ImportJob(db.Model):
    """Import Jobs model class"""
    __tablename__ = 'import_jobs'
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String, nullable=False)
    starts_at = db.Column(db.DateTime(timezone=True))

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    user = db.relationship('User', backref='import_jobs')
    result = db.Column(db.String)
    result_status = db.Column(db.String)

    def __init__(self, task=None, user=None, result=None, result_status=None):
        self.task = task
        self.user = user
        self.result = result
        self.result_status = result_status
        self.starts_at = datetime.now(pytz.utc)

    def __repr__(self):
        return '<ImportJob %d by user %s>' % (self.id, str(self.user))

    def __str__(self):
        return self.__repr__()

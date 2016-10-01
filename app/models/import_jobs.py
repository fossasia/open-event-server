from datetime import datetime

from . import db


class ImportJob(db.Model):
    """Import Jobs model class"""
    __tablename__ = 'import_jobs'
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String, nullable=False)
    start_time = db.Column(db.DateTime)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    user = db.relationship('User', backref='import_jobs')
    result = db.Column(db.String)
    result_status = db.Column(db.String)

    def __init__(self, task=None, user=None, result=None, result_status=None):
        self.task = task
        self.user = user
        self.result = result
        self.result_status = result_status
        self.start_time = datetime.now()

    def __repr__(self):
        return '<ImportJob %d by user %s>' % (self.id, str(self.user))

    def __str__(self):
        return str(self).encode('utf-8')

    def __unicode__(self):
        return self.__repr__()

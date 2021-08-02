from sqlalchemy.sql import func

from app.models import db


class ImportJob(db.Model):
    """Import Jobs model class"""

    __tablename__ = 'import_jobs'
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String, nullable=False)
    starts_at = db.Column(db.DateTime(timezone=True), default=func.now())

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    user = db.relationship('User', backref='import_jobs')
    result = db.Column(db.String)
    result_status = db.Column(db.String)

    def __repr__(self):
        return '<ImportJob %d by user %s>' % (self.id, str(self.user))

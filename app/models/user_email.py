from app.models import db
from app.models.base import SoftDeletionModel


class UserEmail(SoftDeletionModel):
    """user email model class"""

    __tablename__ = 'user_emails'

    id = db.Column(db.Integer, primary_key=True)
    email_address = db.Column(db.String(120), unique=True, nullable=False)
    type = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    user = db.relationship("User", backref="alternate_emails", foreign_keys=[user_id])

    def __repr__(self):
        return '<Email %r>' % self.email_address

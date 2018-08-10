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

    def __init__(self, email_address=None, type=None, user_id=None, deleted_at=None):
        self.email_address = email_address
        self.type = type
        self.user_id = user_id
        self.deleted_at = deleted_at

    def __repr__(self):
        return '<Email %r>' % self.email_address

    def __str__(self):
        return self.__repr__()

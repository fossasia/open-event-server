from app.models import db
from app.models.base import SoftDeletionModel


class UserPermission(SoftDeletionModel):
    """
    User Permissions
    """

    __tablename__ = 'user_permissions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    description = db.Column(db.String)

    unverified_user = db.Column(db.Boolean)
    anonymous_user = db.Column(db.Boolean)

    def __repr__(self):
        return '<UserPerm %r>' % self.name

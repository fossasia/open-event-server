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

    def __init__(self, name, description, unverified_user=False,
                 anonymous_user=False, deleted_at=None):
        self.name = name
        self.description = description
        self.unverified_user = unverified_user
        self.anonymous_user = anonymous_user
        self.deleted_at = deleted_at

    def __repr__(self):
        return '<UserPerm %r>' % self.name

    def __str__(self):
        return self.__repr__()

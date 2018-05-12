from app.models import db


class UserPermission(db.Model):
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
                 anonymous_user=False):
        self.name = name
        self.description = description
        self.unverified_user = unverified_user
        self.anonymous_user = anonymous_user

    def __repr__(self):
        return '<UserPerm %r>' % self.name

    def __str__(self):
        return self.__repr__()

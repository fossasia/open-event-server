from . import db


class UserPermission(db.Model):
    """User Permissions
    """
    __tablename__ = 'user_permissions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    description = db.Column(db.String)

    verified_user = db.Column(db.Boolean)
    unverified_user = db.Column(db.Boolean)
    anonymous_user = db.Column(db.Boolean)

    def __init__(self, name, description, verified_user=False, unverified_user=False,
            anonymous_user=False):
        self.name = name
        self.description = description
        self.verified_user = verified_user
        self.unverified_user = unverified_user
        self.anonymous_user = anonymous_user

    def __repr__(self):
        return '<UserPerm %r>' % self.name

    def __unicode__(self):
        return 'UserPerm %r' % self.name

    def __str__(self):
        return str(self).encode('utf-8')

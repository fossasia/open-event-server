from sqlalchemy import event

from . import db
from user_detail import UserDetail
from .role import user_roles

SPEAKER = 'speaker'
ADMIN = 'admin'
ORGANIZER = 'organizer'
SUPERADMIN = 'super_admin'


class User(db.Model):
    """User model class"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(128))
    reset_password = db.Column(db.String(128))
    salt = db.Column(db.String(128))
    avatar = db.Column(db.String())
    tokens = db.Column(db.Text)
    user_detail = db.relationship("UserDetail", uselist=False, backref="user")
    roles = db.relationship("Role", secondary=user_roles, back_populates="users")

    # Flask-Login integration
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    # Required for administrative interface
    def __unicode__(self):
        return self.username


@event.listens_for(User, 'init')
def receive_init(target, args, kwargs):
    target.user_detail = UserDetail()

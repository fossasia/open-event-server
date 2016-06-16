from sqlalchemy import event

from . import db
from user_detail import UserDetail
from .role import Role
from .users_events_roles import UsersEventsRoles

# System-wide
ADMIN = 'admin'
SUPERADMIN = 'super_admin'

# Event-specific
ORGANIZER = 'organizer'
COORGANIZER = 'coorganizer'
TRACK_ORGANIZER = 'track_organizer'
MODERATOR = 'moderator'
SPEAKER = 'speaker'


class User(db.Model):
    """User model class"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(128))
    role = db.Column(db.String())
    reset_password = db.Column(db.String(128))
    salt = db.Column(db.String(128))
    avatar = db.Column(db.String())
    tokens = db.Column(db.Text)
    user_detail = db.relationship("UserDetail", uselist=False, backref="user")

    def is_role(self, role_name, event_id):
        role = Role.query.filter_by(name=role_name).first()
        uer = UsersEventsRoles.query.filter_by(user=self,
                                               event_id=event_id,
                                               role=role).first()
        if not uer:
            return False
        else:
            return True

    def is_organizer(self, event_id):
        return self.is_role(ORGANIZER, event_id)

    def is_coorganizer(self, event_id):
        return self.is_role(COORGANIZER, event_id)

    def is_track_organizer(self, event_id):
        return self.is_role(TRACK_ORGANIZER, event_id)

    def is_moderator(self, event_id):
        return self.is_role(MODERATOR, event_id)

    def is_speaker(self, event_id):
        return self.is_role(SPEAKER, event_id)

    # def has_perm(self, operation, service_class, service_id):
    #     operations = ('create', 'read', 'update', 'delete',)
    #     try:
    #         index = operations.index(operation)
    #     except ValueError:
    #         # If `operation` arg not in `operations`
    #         raise ValueError('No such operation defined')

    #     try:
    #         service = service_class.get_service_name()
    #     except AttributeError:
    #         # If `service_class` does not have `get_service_name()`
    #         return False

    #     perm = Permission.query.filter_by(user=self,
    #                                       service=service,
    #                                       service_id=service_id).first()
    #     if not perm:
    #         # If no such permission exist
    #         return False

    #     perm_bit = bin(perm.modes)[2:][index]
    #     # e.g. perm.modes = 14, bin()-> '0b1110', [2:]-> '1110', [index]-> '1'
    #     if perm_bit == '1':
    #         return True
    #     else:
    #         return False

    # Flask-Login integration
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def is_super_admin(self):
        return self.role == SUPERADMIN

    def is_admin(self):
        return self.role == ORGANIZER

    # Required for administrative interface
    def __unicode__(self):
        return self.username


@event.listens_for(User, 'init')
def receive_init(target, args, kwargs):
    target.user_detail = UserDetail()

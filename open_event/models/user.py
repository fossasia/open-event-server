from sqlalchemy import event

from . import db
from user_detail import UserDetail
from .role import Role
from .service import Service
from .permission import Permission
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
    reset_password = db.Column(db.String(128))
    salt = db.Column(db.String(128))
    avatar = db.Column(db.String())
    tokens = db.Column(db.Text)
    is_super_admin = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    user_detail = db.relationship("UserDetail", uselist=False, backref="user")

    def _is_role(self, role_name, event_id):
        role = Role.query.filter_by(name=role_name).first()
        uer = UsersEventsRoles.query.filter_by(user=self,
                                               event_id=event_id,
                                               role=role).first()
        if not uer:
            return False
        else:
            return True

    def is_organizer(self, event_id):
        return self._is_role(ORGANIZER, event_id)

    def is_coorganizer(self, event_id):
        return self._is_role(COORGANIZER, event_id)

    def is_track_organizer(self, event_id):
        return self._is_role(TRACK_ORGANIZER, event_id)

    def is_moderator(self, event_id):
        return self._is_role(MODERATOR, event_id)

    def is_speaker(self, event_id):
        return self._is_role(SPEAKER, event_id)

    def _has_perm(self, operation, service_class, event_id):
        # Operation names and their corresponding permission in `Permissions`
        operations = {
            'create': 'can_create',
            'read': 'can_read',
            'update': 'can_update',
            'delete': 'can_delete',
        }
        if operation not in operations.keys():
            raise ValueError('No such operation defined')

        try:
            service_name = service_class.get_service_name()
        except AttributeError:
            # If `service_class` does not have `get_service_name()`
            return False

        service = Service.query.filter_by(name=service_name).first()

        uer_querylist = UsersEventsRoles.query.filter_by(user=self,
                                                         event_id=event_id)
        for uer in uer_querylist:
            role = uer.role
            perm = Permission.query.filter_by(role=role,
                                              service=service).first()
            if getattr(perm, operations[operation]):
                return True

        return False

    def can_create(self, service_class, event_id):
        return self._has_perm('create', service_class, event_id)

    def can_read(self, service_class, event_id):
        return self._has_perm('read', service_class, event_id)

    def can_update(self, service_class, event_id):
        return self._has_perm('update', service_class, event_id)

    def can_delete(self, service_class, event_id):
        return self._has_perm('delete', service_class, event_id)

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

    @property
    def is_staff(self):
        return self.is_super_admin or self.is_admin


@event.listens_for(User, 'init')
def receive_init(target, args, kwargs):
    target.user_detail = UserDetail()

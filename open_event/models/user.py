from sqlalchemy import event
from datetime import datetime

from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from open_event.models.session import Session
from open_event.models.speaker import Speaker
from . import db
from user_detail import UserDetail
from .role import Role
from .service import Service
from .permission import Permission
from .users_events_roles import UsersEventsRoles
from .notifications import Notification

# System-wide
ADMIN = 'admin'
SUPERADMIN = 'super_admin'

# Event-specific
ORGANIZER = 'organizer'
COORGANIZER = 'coorganizer'
TRACK_ORGANIZER = 'track_organizer'
MODERATOR = 'moderator'


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
    is_verified = db.Column(db.Boolean, default=False)
    signup_time = db.Column(db.DateTime)
    last_access_time = db.Column(db.DateTime)
    user_detail = db.relationship("UserDetail", uselist=False, backref="user")
    created_date = db.Column(db.DateTime, default=datetime.now())

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

    def is_speaker_at_session(self, session_id):
        try:
            session = Session.query.filter(Session.speakers.any(Speaker.user_id == self.id)).filter(
                Session.id == session_id).one()
            if session:
                return True
            else:
                return False
        except MultipleResultsFound, e:
            return False
        except NoResultFound, e:
            return False

    def is_speaker_at_event(self, event_id):
        try:
            session = Session.query.filter(Session.speakers.any(Speaker.user_id == self.id)).filter(
                Session.event_id == event_id).first()
            if session:
                return True
            else:
                return False
        except MultipleResultsFound, e:
            return False
        except NoResultFound, e:
            return False

    # Flask-Login integration
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    @property
    def is_staff(self):
        return self.is_super_admin or self.is_admin

    def get_unread_notif_count(self):
        return len(Notification.query.filter_by(user=self,
                                                has_read=False).all())

    # update last access time
    def update_lat(self):
        self.last_access_time = datetime.now()

    def __repr__(self):
        return '<User %r>' % self.email

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.email


@event.listens_for(User, 'init')
def receive_init(target, args, kwargs):
    target.user_detail = UserDetail()
    target.signup_time = datetime.now()

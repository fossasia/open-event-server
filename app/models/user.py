from sqlalchemy import event, desc
from datetime import datetime

import humanize
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from flask import url_for

from app.models.session import Session
from app.models.speaker import Speaker
from . import db
from user_detail import UserDetail
from .role import Role
from .service import Service
from .permission import Permission
from .system_role import UserSystemRole
from .user_permissions import UserPermission
from .users_events_roles import UsersEventsRoles as UER
from .notifications import Notification

# System-wide
ADMIN = 'admin'
SUPERADMIN = 'super_admin'

SYS_ROLES_LIST = [
    ADMIN,
    SUPERADMIN,
]

# Event-specific
ORGANIZER = 'organizer'
COORGANIZER = 'coorganizer'
TRACK_ORGANIZER = 'track_organizer'
MODERATOR = 'moderator'
ATTENDEE = 'attendee'


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
    in_trash = db.Column(db.Boolean, default=False)
    user_detail = db.relationship("UserDetail", uselist=False, backref="user")
    created_date = db.Column(db.DateTime, default=datetime.now())
    trash_date = db.Column(db.DateTime)

    # User Permissions
    def can_publish_event(self):
        """Checks if User can publish an event
        """
        perm = UserPermission.query.filter_by(name='publish_event').first()
        if not perm:
            return self.is_verified

        if self.is_verified:
            return perm.verified_user
        else:
            return perm.unverified_user

    def can_create_event(self):
        """Checks if User can create an event
        """
        perm = UserPermission.query.filter_by(name='create_event').first()
        if not perm:
            return self.is_verified

        if self.is_verified:
            return perm.verified_user
        else:
            return perm.unverified_user

    def has_role(self, event_id):
        """Checks if user has any of the Roles at an Event.
        Exclude Attendee Role.
        """
        attendee_role = Role.query.filter_by(name=ATTENDEE).first()
        uer = UER.query.filter(UER.user == self, UER.event_id == event_id,
            UER.role != attendee_role).first()
        if uer is None:
            return False
        else:
            return True

    def _is_role(self, role_name, event_id):
        """Checks if a user has a particular Role at an Event.
        """
        role = Role.query.filter_by(name=role_name).first()
        uer = UER.query.filter_by(user=self,
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

    def is_attendee(self, event_id):
        return self._is_role(ATTENDEE, event_id)

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

        if self.is_super_admin:
            return True

        service = Service.query.filter_by(name=service_name).first()

        uer_querylist = UER.query.filter_by(user=self,
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
        except MultipleResultsFound:
            return False
        except NoResultFound:
            return False

    def is_speaker_at_event(self, event_id):
        try:
            session = Session.query.filter(Session.speakers.any(Speaker.user_id == self.id)).filter(
                Session.event_id == event_id).first()
            if session:
                return True
            else:
                return False
        except MultipleResultsFound:
            return False
        except NoResultFound:
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

    def is_sys_role(self, role_id):
        """Check if a user has a Custom System Role assigned.
        `role_id` is id of a `CustomSysRole` instance.
        """
        role = UserSystemRole.query.filter_by(user=self, role_id=role_id).first()
        return bool(role)

    def can_access_panel(self, panel_name):
        """Check if user can access an Admin Panel
        """
        if self.is_staff:
            return True

        custom_sys_roles = UserSystemRole.query.filter_by(user=self)
        for role in custom_sys_roles:
            if role.can_access(panel_name):
                return True

        return False

    def get_unread_notif_count(self):
        return len(Notification.query.filter_by(user=self,
                                                has_read=False).all())

    def get_unread_notifs(self):
        """Get unread notifications with titles, humanized receiving time
        and Mark-as-read links.
        """
        notifs = []
        unread_notifs = Notification.query.filter_by(user=self, has_read=False).order_by(
            desc(Notification.received_at))
        for notif in unread_notifs:
            notifs.append({
                'title': notif.title,
                'received_at': humanize.naturaltime(datetime.now() - notif.received_at),
                'mark_read': url_for('notifications.mark_as_read', notification_id=notif.id)
            })

        return notifs

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

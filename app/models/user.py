import random
from datetime import datetime

import humanize
import pytz
from citext import CIText
from coolname import generate
from flask import url_for
from flask_scrypt import generate_password_hash, generate_random_salt
from slugify import slugify
from sqlalchemy import desc, event
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.sql import func

from app.api.helpers.db import get_count
from app.api.helpers.utilities import get_serializer
from app.models import db
from app.models.base import SoftDeletionModel
from app.models.custom_system_role import UserSystemRole
from app.models.event import Event
from app.models.helpers.versioning import clean_html, clean_up_string
from app.models.notification import Notification
from app.models.panel_permission import PanelPermission
from app.models.permission import Permission
from app.models.role import Role
from app.models.service import Service
from app.models.session import Session
from app.models.speaker import Speaker
from app.models.user_permission import UserPermission
from app.models.users_events_role import UsersEventsRoles as UER

# System-wide
ADMIN = 'admin'
SUPERADMIN = 'super_admin'

MARKETER = 'Marketer'
SALES_ADMIN = 'Sales Admin'

SYS_ROLES_LIST = [
    ADMIN,
    SUPERADMIN,
]

# Event-specific
TRACK_ORGANIZER = 'track_organizer'
MODERATOR = 'moderator'
REGISTRAR = 'registrar'


class User(SoftDeletionModel):
    """User model class"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    _email = db.Column(CIText, unique=True, nullable=False)
    _password = db.Column(db.String(128), nullable=False)
    facebook_id = db.Column(db.BigInteger, unique=True, nullable=True, name='facebook_id')
    facebook_login_hash = db.Column(db.String, nullable=True)
    reset_password = db.Column(db.String(128))
    salt = db.Column(db.String(128))
    avatar_url = db.Column(db.String)
    tokens = db.Column(db.Text)
    first_name = db.Column(db.String, nullable=True)
    last_name = db.Column(db.String, nullable=True)
    details = db.Column(db.String)
    contact = db.Column(db.String)
    facebook_url = db.Column(db.String)
    twitter_url = db.Column(db.String)
    instagram_url = db.Column(db.String)
    google_plus_url = db.Column(db.String)
    original_image_url = db.Column(db.String, nullable=True, default=None)
    thumbnail_image_url = db.Column(db.String)
    small_image_url = db.Column(db.String)
    icon_image_url = db.Column(db.String)
    is_super_admin = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_sales_admin = db.Column(db.Boolean, default=False)
    is_marketer = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    is_blocked = db.Column(db.Boolean, nullable=False, default=False)
    is_profile_public = db.Column(
        db.Boolean, nullable=False, default=False, server_default='False'
    )
    public_name = db.Column(db.String)
    was_registered_with_order = db.Column(db.Boolean, default=False)
    last_accessed_at = db.Column(db.DateTime(timezone=True))
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    # Event Invoice Details
    billing_contact_name = db.Column(db.String)
    billing_phone = db.Column(db.String)
    billing_state = db.Column(db.String)
    billing_country = db.Column(db.String)
    billing_tax_info = db.Column(db.String)
    company = db.Column(db.String)
    billing_address = db.Column(db.String)
    billing_city = db.Column(db.String)
    language_prefrence = db.Column(db.String)
    billing_zip_code = db.Column(db.String)
    billing_additional_info = db.Column(db.String)

    rocket_chat_token = db.Column(db.String)

    # relationships
    speaker = db.relationship('Speaker', backref="user")
    favourite_events = db.relationship('UserFavouriteEvent', backref="user")
    session = db.relationship('Session', backref="user")
    feedback = db.relationship('Feedback', backref="user")
    access_codes = db.relationship('AccessCode', backref="user")
    discount_codes = db.relationship('DiscountCode', backref="user")
    marketer_events = db.relationship(
        'Event',
        viewonly=True,
        secondary='join(UserSystemRole, CustomSysRole,'
        ' and_(CustomSysRole.id == UserSystemRole.role_id, CustomSysRole.name == "Marketer"))',
        primaryjoin='UserSystemRole.user_id == User.id',
        secondaryjoin='Event.id == UserSystemRole.event_id',
    )
    sales_admin_events = db.relationship(
        'Event',
        viewonly=True,
        secondary='join(UserSystemRole, CustomSysRole,'
        ' and_(CustomSysRole.id == UserSystemRole.role_id, CustomSysRole.name == "Sales Admin"))',
        primaryjoin='UserSystemRole.user_id == User.id',
        secondaryjoin='Event.id == UserSystemRole.event_id',
    )

    @hybrid_property
    def password(self):
        """
        Hybrid property for password
        :return:
        """
        return self._password

    @password.setter
    def password(self, password):
        """
        Setter for _password, saves hashed password, salt and reset_password string
        :param password:
        :return:
        """
        salt = str(generate_random_salt(), 'utf-8')
        self._password = str(generate_password_hash(password, salt), 'utf-8')
        hash_ = random.getrandbits(128)
        self.reset_password = str(hash_)
        self.salt = salt

    @hybrid_property
    def email(self):
        """
        Hybrid property for email
        :return:
        """
        return self._email

    @email.setter
    def email(self, email):
        """
        Setter for _email,
        set user to 'not verified' if email is updated
        :param email:
        :return:
        """
        if self._email != email:
            self._email = email
            self.is_verified = False

    # User Permissions
    def can_publish_event(self):
        """
        Checks if User can publish an event
        """
        perm = UserPermission.query.filter_by(name='publish_event').first()
        if not perm:
            return self.is_verified

        if self.is_verified is False:
            return perm.unverified_user

        return True

    def can_create_event(self):
        """
        Checks if User can create an event
        """
        perm = UserPermission.query.filter_by(name='create_event').first()
        if not perm:
            return self.is_verified

        if self.is_verified is False:
            return perm.unverified_user

        return True

    def _is_role(self, role_name, event_id=None):
        """
        Checks if a user has a particular Role at an Event.
        """
        from app.models.users_groups_role import UsersGroupsRoles

        role = Role.query.filter_by(name=role_name).first()
        uer = UER.query.filter_by(user=self, role=role)
        ugr = UsersGroupsRoles.query.filter_by(user=self, role=role, accepted=True)
        if event_id:
            uer = uer.filter_by(event_id=event_id)
            event = Event.query.get(event_id)
            # Validation to ensure event is not None
            if event is not None and event.group is not None:
                ugr = ugr.filter_by(group=event.group)
        return bool(uer.first() or ugr.first())

    def is_owner(self, event_id):
        return self._is_role(Role.OWNER, event_id)

    def is_organizer(self, event_id):
        return self._is_role(Role.ORGANIZER, event_id)

    def is_coorganizer(self, event_id):
        return self._is_role(Role.COORGANIZER, event_id)

    def is_track_organizer(self, event_id):
        return self._is_role(TRACK_ORGANIZER, event_id)

    def is_moderator(self, event_id):
        return self._is_role(MODERATOR, event_id)

    def is_registrar(self, event_id):
        return self._is_role(REGISTRAR, event_id)

    def has_event_access(self, event_id):
        return (
            self._is_role(Role.OWNER, event_id)
            or self._is_role(Role.ORGANIZER, event_id)
            or self._is_role(Role.COORGANIZER, event_id)
        )

    @hybrid_property
    def is_user_owner(self):
        return self._is_role(Role.OWNER)

    @hybrid_property
    def is_user_organizer(self):
        return self._is_role(Role.ORGANIZER)

    @hybrid_property
    def is_user_coorganizer(self):
        return self._is_role(Role.COORGANIZER)

    @hybrid_property
    def is_user_track_organizer(self):
        return self._is_role(TRACK_ORGANIZER)

    @hybrid_property
    def is_user_moderator(self):
        return self._is_role(MODERATOR)

    @hybrid_property
    def is_user_registrar(self):
        return self._is_role(REGISTRAR)

    def _has_perm(self, operation, service_class, event_id):
        # Operation names and their corresponding permission in `Permissions`
        operations = {
            'create': 'can_create',
            'read': 'can_read',
            'update': 'can_update',
            'delete': 'can_delete',
        }
        if operation not in list(operations.keys()):
            raise ValueError('No such operation defined')

        try:
            service_name = service_class.get_service_name()
        except AttributeError:
            # If `service_class` does not have `get_service_name()`
            return False

        if self.is_super_admin:
            return True

        service = Service.query.filter_by(name=service_name).first()

        uer_querylist = UER.query.filter_by(user=self, event_id=event_id)
        for uer in uer_querylist:
            role = uer.role
            perm = Permission.query.filter_by(role=role, service=service).first()
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
            session = (
                Session.query.filter(Session.speakers.any(Speaker.user_id == self.id))
                .filter(Session.id == session_id)
                .one()
            )
            return bool(session)
        except MultipleResultsFound:
            return False
        except NoResultFound:
            return False

    def is_speaker_at_event(self, event_id):
        try:
            session = (
                Session.query.filter(Session.speakers.any(Speaker.user_id == self.id))
                .filter(Session.event_id == event_id)
                .first()
            )
            return bool(session)
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

    def is_correct_password(self, password):
        salt = self.salt
        password = str(generate_password_hash(password, salt), 'utf-8')
        if password == self._password:
            return True
        return False

    @property
    def is_staff(self):
        return self.is_super_admin or self.is_admin

    def is_sys_role(self, role_id):
        """
        Check if a user has a Custom System Role assigned.
        `role_id` is id of a `CustomSysRole` instance.
        """
        role = UserSystemRole.query.filter_by(user=self, role_id=role_id).first()
        return bool(role)

    def first_access_panel(self):
        """
        Check if the user is assigned a Custom Role or not
        This checks if there is an entry containing the current user in the `user_system_roles` table
        returns panel name if exists otherwise false
        """
        custom_role = UserSystemRole.query.filter_by(user=self).first()
        if not custom_role:
            return False
        perm = PanelPermission.query.filter(
            PanelPermission.custom_system_roles.any(id=custom_role.role_id)
        ).first()
        if not perm:
            return False
        return perm.panel_name

    def can_access_panel(self, panel_name):
        """
        Check if user can access an Admin Panel
        """
        if self.is_staff:
            return True

        custom_sys_roles = UserSystemRole.query.filter_by(user=self)
        for custom_role in custom_sys_roles:
            if custom_role.role.can_access(panel_name):
                return True

        return False

    def get_unread_notif_count(self):
        return get_count(Notification.query.filter_by(user=self, is_read=False))

    def get_unread_notifs(self):
        """
        Get unread notifications with titles, humanized receiving time
        and Mark-as-read links.
        """
        notifs = []
        unread_notifs = Notification.query.filter_by(user=self, is_read=False).order_by(
            desc(Notification.received_at)
        )
        for notif in unread_notifs:
            notifs.append(
                {
                    'title': notif.title,
                    'received_at': humanize.naturaltime(
                        datetime.now(pytz.utc) - notif.received_at
                    ),
                    'mark_read': url_for(
                        'notifications.mark_as_read', notification_id=notif.id
                    ),
                }
            )

        return notifs

    # update last access time
    def update_lat(self):
        self.last_accessed_at = datetime.now()

    # Deprecated
    @property
    def fullname(self):
        return self.full_name

    @property
    def full_name(self):
        return ' '.join(filter(None, [self.first_name, self.last_name]))

    def get_full_billing_address(self, sep: str = '\n') -> str:
        return sep.join(
            filter(
                None,
                [
                    self.billing_address,
                    self.billing_city,
                    self.billing_state,
                    self.billing_zip_code,
                    self.billing_country,
                ],
            )
        )

    full_billing_address = property(get_full_billing_address)

    @property
    def anonymous_name(self):
        return ' '.join(map(lambda x: x.capitalize(), generate(2)))

    @property
    def rocket_chat_username(self):
        name = self.public_name or self.full_name or f'user_{self.id}'
        return slugify(name, word_boundary=True, max_length=32, separator='.')

    @property
    def rocket_chat_password(self):
        return get_serializer().dumps(f'rocket_chat_user_{self.id}')

    @property
    def is_rocket_chat_registered(self) -> bool:
        return self.rocket_chat_token is not None

    def __repr__(self):
        return '<User %r>' % self.email

    def __setattr__(self, name, value):
        if name == 'details':
            super().__setattr__(name, clean_html(clean_up_string(value)))
        else:
            super().__setattr__(name, value)


@event.listens_for(User, 'init')
def receive_init(target, args, kwargs):
    target.signup_at = datetime.now(pytz.utc)

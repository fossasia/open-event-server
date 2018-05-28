from app import current_app
from app.models import db
from app.api.helpers.db import get_or_create  # , save_to_db

# Admin message settings
from app.api.helpers.system_mails import MAILS
from app.models.message_setting import MessageSettings

# Event Role-Service Permissions
from app.models.role import Role
from app.models.service import Service
from app.models.permission import Permission

from app.models.track import Track
from app.models.session import Session
from app.models.speaker import Speaker
from app.models.sponsor import Sponsor
from app.models.microlocation import Microlocation

from app.models.user import ORGANIZER, COORGANIZER, TRACK_ORGANIZER, MODERATOR, ATTENDEE, REGISTRAR

# Admin Panel Permissions
from app.models.panel_permission import PanelPermission
from app.models.custom_system_role import CustomSysRole

from app.models.setting import Setting
from app.models.module import Module

# User Permissions
from app.models.user_permission import UserPermission
SALES = 'sales'


def create_roles():
    get_or_create(Role, name=ORGANIZER, title_name='Organizer')
    get_or_create(Role, name=COORGANIZER, title_name='Co-organizer')
    get_or_create(Role, name=TRACK_ORGANIZER, title_name='Track Organizer')
    get_or_create(Role, name=MODERATOR, title_name='Moderator')
    get_or_create(Role, name=ATTENDEE, title_name='Attendee')
    get_or_create(Role, name=REGISTRAR, title_name='Registrar')


def create_services():
    track = Track.get_service_name()
    session = Session.get_service_name()
    speaker = Speaker.get_service_name()
    sponsor = Sponsor.get_service_name()
    microlocation = Microlocation.get_service_name()

    get_or_create(Service, name=track)
    get_or_create(Service, name=session)
    get_or_create(Service, name=speaker)
    get_or_create(Service, name=sponsor)
    get_or_create(Service, name=microlocation)


def create_settings():
    get_or_create(Setting, app_name='Open Event')


def create_modules():
    get_or_create(Module, donation_include=False)


def create_permissions():
    orgr = Role.query.get(1)
    coorgr = Role.query.get(2)
    track_orgr = Role.query.get(3)
    mod = Role.query.get(4)

    track = Service.query.get(1)
    session = Service.query.get(2)
    speaker = Service.query.get(3)
    sponsor = Service.query.get(4)
    microlocation = Service.query.get(5)

    # For ORGANIZER
    # All four permissions set to True
    get_or_create(Permission, role=orgr, service=track)
    get_or_create(Permission, role=orgr, service=session)
    get_or_create(Permission, role=orgr, service=speaker)
    get_or_create(Permission, role=orgr, service=sponsor)
    get_or_create(Permission, role=orgr, service=microlocation)

    # For COORGANIZER
    perm, _ = get_or_create(Permission, role=coorgr, service=track)
    perm.can_create, perm.can_delete = False, False
    db.session.add(perm)

    perm, _ = get_or_create(Permission, role=coorgr, service=session)
    perm.can_create, perm.can_delete = False, False
    db.session.add(perm)

    perm, _ = get_or_create(Permission, role=coorgr, service=speaker)
    perm.can_create, perm.can_delete = False, False
    db.session.add(perm)

    perm, _ = get_or_create(Permission, role=coorgr, service=sponsor)
    perm.can_create, perm.can_delete = False, False
    db.session.add(perm)

    perm, _ = get_or_create(Permission, role=coorgr, service=microlocation)
    perm.can_create, perm.can_delete = False, False
    db.session.add(perm)

    # For TRACK_ORGANIZER
    perm, _ = get_or_create(Permission, role=track_orgr, service=track)
    db.session.add(perm)

    # For MODERATOR
    perm, _ = get_or_create(Permission, role=mod, service=track)
    perm.can_create, perm.can_update, perm.can_delete = False, False, False
    db.session.add(perm)


def create_custom_sys_roles():
    role, _ = get_or_create(CustomSysRole, name='Sales Admin')
    db.session.add(role)
    role, _ = get_or_create(CustomSysRole, name='Marketer')
    db.session.add(role)


def create_panel_permissions():
    sales_admin = CustomSysRole.query.filter_by(name='Sales Admin').first()
    perm, _ = get_or_create(PanelPermission, panel_name=SALES, role=sales_admin)
    db.session.add(perm)
    marketer = CustomSysRole.query.filter_by(name='Marketer').first()
    perm, _ = get_or_create(PanelPermission, panel_name=SALES, role=marketer)
    db.session.add(perm)


def create_user_permissions():
    # Publish Event
    user_perm, _ = get_or_create(UserPermission, name='publish_event',
                                 description='Publish event (make event live)')
    user_perm.verified_user = True
    db.session.add(user_perm)

    # Create Event
    user_perm, _ = get_or_create(UserPermission, name='create_event',
                                 description='Create event')
    user_perm.verified_user, user_perm.unverified_user = True, True
    db.session.add(user_perm)


def create_admin_message_settings():
    default_mails = ["Next Event",
                     "Session Schedule Change",
                     "User email",
                     "Invitation For Papers",
                     "After Event",
                     "Ticket(s) Purchased",
                     "Session Accept or Reject",
                     "Event Published",
                     "Event Export Failed",
                     "Event Exported",
                     "Event Role Invitation",
                     "New Session Proposal"]
    for mail in MAILS:
        if mail in default_mails:
            get_or_create(MessageSettings, action=mail, mail_status=1, notification_status=1, user_control_status=1)
        else:
            get_or_create(MessageSettings, action=mail, mail_status=0, notification_status=0, user_control_status=0)


def populate():
    """
    Create defined Roles, Services and Permissions.
    """
    print('Creating roles...')
    create_roles()
    print('Creating services...')
    create_services()
    print('Creating permissions...')
    create_permissions()
    print('Creating custom system roles...')
    create_custom_sys_roles()
    print('Creating admin panel permissions...')
    create_panel_permissions()
    print('Creating user permissions...')
    create_user_permissions()
    print('Creating settings...')
    create_settings()
    print('Creating modules...')
    create_modules()
    print('Creating admin message settings...')
    create_admin_message_settings()


def populate_without_print():
    """
    Create defined Roles, Services and Permissions.
    """
    create_roles()
    create_services()
    create_permissions()
    create_custom_sys_roles()
    create_panel_permissions()
    create_user_permissions()
    create_admin_message_settings()

    db.session.commit()


if __name__ == '__main__':
    with current_app.app_context():
        populate()

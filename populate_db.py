from app import current_app
from app.models import db
from app.helpers.data import get_or_create#, save_to_db

# Event Role-Service Permissions
from app.models.role import Role
from app.models.service import Service
from app.models.permission import Permission

from app.models.track import Track
from app.models.session import Session
from app.models.speaker import Speaker
from app.models.sponsor import Sponsor
from app.models.microlocation import Microlocation

from app.models.user import ORGANIZER, COORGANIZER, TRACK_ORGANIZER, MODERATOR, ATTENDEE

# Admin Panel Permissions
from app.models.admin_panels import PanelPermission
from app.models.user import SUPERADMIN, ADMIN, SALES_ADMIN
from app.views.admin.super_admin.super_admin_base import PANEL_LIST, SALES

# User Permissions
from app.models.user_permissions import UserPermission


def create_roles():
    get_or_create(Role, name=ORGANIZER, title_name='Organizer')
    get_or_create(Role, name=COORGANIZER, title_name='Co-organizer')
    get_or_create(Role, name=TRACK_ORGANIZER, title_name='Track Organizer')
    get_or_create(Role, name=MODERATOR, title_name='Moderator')
    get_or_create(Role, name=ATTENDEE, title_name='Attendee')


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


def create_panel_permissions():
    # For Super Admin
    for panel in PANEL_LIST:
        panel_perm, _ = get_or_create(PanelPermission, role_name=SUPERADMIN, panel_name=panel)
        panel_perm.can_access = True
        db.session.add(panel_perm)

    # For Admin
    for panel in PANEL_LIST:
        panel_perm, _ = get_or_create(PanelPermission, role_name=ADMIN, panel_name=panel)
        panel_perm.can_access = True
        db.session.add(panel_perm)

    # For Sales Admin
    panel_perm, _ = get_or_create(PanelPermission, role_name=SALES_ADMIN, panel_name=SALES)
    panel_perm.can_access = True
    db.session.add(panel_perm)


def create_user_permissions():
    user_perm, _ = get_or_create(UserPermission, name='publish_event',
        description='Publish event (make event live)')
    user_perm.verified_user = True
    db.session.add(user_perm)


def populate():
    """
    Create defined Roles, Services and Permissions.
    """
    print
    print 'Creating roles...'
    create_roles()
    print 'Creating services...'
    create_services()
    print 'Creating permissions...'
    create_permissions()
    print 'Creating admin panel permissions...'
    create_panel_permissions()
    print 'Creating user permissions...'
    create_user_permissions()

    db.session.commit()


if __name__ == '__main__':
    with current_app.app_context():
        populate()

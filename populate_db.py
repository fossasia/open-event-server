from app import current_app

from app.models.role import Role
from app.models.service import Service
from app.models.permission import Permission

from app.models.track import Track
from app.models.session import Session
from app.models.speaker import Speaker
from app.models.sponsor import Sponsor
from app.models.microlocation import Microlocation

from app.helpers.data import get_or_create
from app.models.user import ORGANIZER, COORGANIZER, TRACK_ORGANIZER, MODERATOR, ATTENDEE

# Admin Panels
from app.models.admin_panels import PanelPermission
from app.models.user import SUPERADMIN, ADMIN
from app.views.admin.super_admin.super_admin_base import PANEL_LIST


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
    get_or_create(Permission, role=orgr, service=track, can_create=True, can_read=True, can_update=True, can_delete=True)
    get_or_create(Permission, role=orgr, service=session, can_create=True, can_read=True, can_update=True, can_delete=True)
    get_or_create(Permission, role=orgr, service=speaker, can_create=True, can_read=True, can_update=True, can_delete=True)
    get_or_create(Permission, role=orgr, service=sponsor, can_create=True, can_read=True, can_update=True, can_delete=True)
    get_or_create(Permission, role=orgr, service=microlocation, can_create=True, can_read=True, can_update=True, can_delete=True)

    # For COORGANIZER
    get_or_create(Permission, role=coorgr, service=track, can_create=False, can_read=True, can_update=True, can_delete=False)
    get_or_create(Permission, role=coorgr, service=session, can_create=False, can_read=True, can_update=True, can_delete=False)
    get_or_create(Permission, role=coorgr, service=speaker, can_create=False, can_read=True, can_update=True, can_delete=False)
    get_or_create(Permission, role=coorgr, service=sponsor, can_create=False, can_read=True, can_update=True, can_delete=False)
    get_or_create(Permission, role=coorgr, service=microlocation, can_create=False, can_read=True, can_update=True, can_delete=False)

    # For TRACK_ORGANIZER
    get_or_create(Permission, role=track_orgr, service=track, can_create=False, can_read=True, can_update=True, can_delete=False)

    # For MODERATOR
    get_or_create(Permission, role=mod, service=track, can_create=False, can_read=True, can_update=False, can_delete=False)


def create_panel_permissions():
    # For Super Admin
    for panel in PANEL_LIST:
        get_or_create(PanelPermission, role_name=SUPERADMIN, panel_name=panel, can_access=True)
    # For Admin
    for panel in PANEL_LIST:
        get_or_create(PanelPermission, role_name=ADMIN, panel_name=panel, can_access=True)


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


if __name__ == '__main__':
    with current_app.app_context():
        populate()

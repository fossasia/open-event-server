import re
import sys

from open_event import current_app
from open_event.models import db
from open_event.models.role import Role
from open_event.models.service import Service
from open_event.models.permission import Permission

from open_event.models.track import Track
from open_event.models.session import Session
from open_event.models.speaker import Speaker
from open_event.models.sponsor import Sponsor
from open_event.models.microlocation import Microlocation

from open_event.helpers.data import DataManager, save_to_db
from open_event.models.user import ORGANIZER, COORGANIZER, TRACK_ORGANIZER, MODERATOR, SPEAKER


def _validate_email(email):
    if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
        print '\nInvalid email address'
        sys.exit(1)


def _validate_password(password):
    if len(password) < 4:
        print '\nPassword should have minimum 4 characters'
        sys.exit(1)


def create_default_user():
    print "Your login is 'super_admin'."
    email = raw_input("Enter email for super_admin    : ")
    _validate_email(email)
    password = raw_input("Enter password for super_admin : ")
    _validate_password(password)
    DataManager.create_super_admin(email, password)


def create_roles():
    save_to_db(Role(ORGANIZER), 'Role saved')
    save_to_db(Role(COORGANIZER), 'Role saved')
    save_to_db(Role(TRACK_ORGANIZER), 'Role saved')
    save_to_db(Role(MODERATOR), 'Role saved')
    save_to_db(Role(SPEAKER), 'Role saved')


def create_services():
    track = Track.get_service_name()
    session = Session.get_service_name()
    speaker = Speaker.get_service_name()
    sponsor = Sponsor.get_service_name()
    microlocation = Microlocation.get_service_name()

    save_to_db(Service(track), 'Service saved')
    save_to_db(Service(session), 'Service saved')
    save_to_db(Service(speaker), 'Service saved')
    save_to_db(Service(sponsor), 'Service saved')
    save_to_db(Service(microlocation), 'Service saved')


def create_permissions():
    orgr = Role.query.get(1)
    coorgr = Role.query.get(2)
    track_orgr = Role.query.get(3)
    mod = Role.query.get(4)
    spkr = Role.query.get(5)

    track = Service.query.get(1)
    session = Service.query.get(2)
    speaker = Service.query.get(3)
    sponsor = Service.query.get(4)
    microlocation = Service.query.get(5)

    # For ORGANIZER
    perm = Permission(orgr, track, True, True, True, True)
    save_to_db(perm, 'Permission saved')
    perm = Permission(orgr, session, True, True, True, True)
    save_to_db(perm, 'Permission saved')
    perm = Permission(orgr, speaker, True, True, True, True)
    save_to_db(perm, 'Permission saved')
    perm = Permission(orgr, sponsor, True, True, True, True)
    save_to_db(perm, 'Permission saved')
    perm = Permission(orgr, microlocation, True, True, True, True)
    save_to_db(perm, 'Permission saved')

    # For COORGANIZER
    perm = Permission(coorgr, track, False, True, True, False)
    save_to_db(perm, 'Permission saved')
    perm = Permission(coorgr, session, False, True, True, False)
    save_to_db(perm, 'Permission saved')
    perm = Permission(coorgr, speaker, False, True, True, False)
    save_to_db(perm, 'Permission saved')
    perm = Permission(coorgr, sponsor, False, True, True, False)
    save_to_db(perm, 'Permission saved')
    perm = Permission(coorgr, microlocation, False, True, True, False)
    save_to_db(perm, 'Permission saved')

    # For TRACK_ORGANIZER
    perm = Permission(track_orgr, track, False, True, True, False)
    save_to_db(perm, 'Permission saved')

    # For MODERATOR
    perm = Permission(mod, track, False, True, False, False)
    save_to_db(perm, 'Permission saved')

    # For SPEAKER
    # ?


if __name__ == "__main__":
    with current_app.app_context():
        db.create_all()
        create_default_user()
        print
        print 'Creating roles...'
        create_roles()
        print 'Creating services...'
        create_services()
        print 'Creating permissions...'
        create_permissions()

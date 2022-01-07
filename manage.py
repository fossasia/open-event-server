import logging
import os

from flask_migrate import MigrateCommand, stamp
from flask_script import Manager
from sqlalchemy import or_
from sqlalchemy.engine import reflection

from app.api.helpers.db import save_to_db
from app.instance import current_app as app
from app.api.helpers.tasks import (
    resize_event_images_task,
    resize_speaker_images_task,
    resize_exhibitor_images_task,
    resize_group_images_task,
)
from app.models import db
from app.models.event import Event, get_new_event_identifier
from app.models.group import Group
from app.models.speaker import Speaker
from app.models.exhibitor import Exhibitor
from populate_db import populate
from tests.all.integration.auth_helper import create_super_admin

logger = logging.getLogger(__name__)

manager = Manager(app)
manager.add_command('db', MigrateCommand)


@manager.command
def list_routes():
    import urllib

    output = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        line = urllib.parse.unquote(f"{rule.endpoint:50s} {methods:20s} {rule}")
        output.append(line)

    for line in sorted(output):
        print(line)


@manager.command
def add_event_identifier():
    events = Event.query.all()
    for event in events:
        event.identifier = get_new_event_identifier()
        save_to_db(event)


@manager.command
def fix_exhibitor_images():
    exhibitors = Exhibitor.query.filter(
        Exhibitor.banner_url.isnot(None), Exhibitor.thumbnail_image_url == None
    ).all()
    print(f'Resizing images of { len(exhibitors) } exhibitors...')
    for exhibitor in exhibitors:
        print(f'Resizing Exhibitor { exhibitor.id }')
        resize_exhibitor_images_task.delay(exhibitor.id, exhibitor.banner_url)


@manager.command
def fix_group_images():
    groups = Group.query.filter(
        Group.banner_url.isnot(None), Group.thumbnail_image_url == None
    ).all()
    print(f'Resizing images of { len(groups) } groups...')
    for group in groups:
        print(f'Resizing image of Group { group.id } ')
        resize_group_images_task.delay(group.id, group.banner_url)


@manager.command
def fix_event_and_speaker_images():
    events = Event.query.filter(
        Event.original_image_url.isnot(None),
        or_(
            Event.thumbnail_image_url == None,
            Event.large_image_url == None,
            Event.icon_image_url == None,
        ),
    ).all()
    logger.info('Resizing images of %s events...', len(events))
    for event in events:
        logger.info('Resizing Event %s', event.id)
        resize_event_images_task.delay(event.id, event.original_image_url)

    speakers = Speaker.query.filter(
        Speaker.photo_url.isnot(None),
        or_(
            Speaker.icon_image_url == None,
            Speaker.small_image_url == None,
            Speaker.thumbnail_image_url == None,
        ),
    ).all()

    logger.info('Resizing images of %s speakers...', len(speakers))
    for speaker in speakers:
        logging.info('Resizing Speaker %s', speaker.id)
        resize_speaker_images_task.delay(speaker.id, speaker.photo_url)


@manager.command
def fix_digit_identifier():
    events = Event.query.filter(Event.identifier.op('~')(r'^[0-9\.]+$')).all()
    for event in events:
        event.identifier = get_new_event_identifier()
        db.session.add(event)
    db.session.commit()


@manager.option(
    '-c', '--credentials', help='Super admin credentials. Eg. username:password'
)
def initialize_db(credentials):
    with app.app_context():
        populate_data = True
        inspector = reflection.Inspector.from_engine(db.engine)
        table_name = 'events'
        table_names = inspector.get_table_names()
        print("[LOG] Existing tables:")
        print("[LOG] " + ','.join(table_names))
        if table_name not in table_names:
            print("[LOG] Table not found. Attempting creation")
            try:
                db.engine.execute('create extension if not exists citext')
                db.create_all()
                stamp()
            except Exception:
                populate_data = False
                print(
                    "[LOG] Could not create tables. Either database does not exist or tables already created"
                )
            if populate_data:
                credentials = credentials.split(":")
                admin_email = os.environ.get('SUPER_ADMIN_EMAIL', credentials[0])
                admin_password = os.environ.get('SUPER_ADMIN_PASSWORD', credentials[1])
                create_super_admin(admin_email, admin_password)
                populate()
        else:
            print("[LOG] Tables already exist. Skipping data population & creation.")


@manager.command
def prepare_db(credentials='open_event_test_user@fossasia.org:fossasia'):
    with app.app_context():
        initialize_db(credentials)


if __name__ == "__main__":
    manager.run()

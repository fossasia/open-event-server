import argparse
import logging
import os

import click
from flask.cli import with_appcontext
from flask_migrate import stamp
from sqlalchemy import or_
from sqlalchemy.engine import reflection

from ..api.helpers.db import save_to_db
from ..base import app
from ..api.helpers.tasks import (
    resize_event_images_task,
    resize_speaker_images_task,
    resize_exhibitor_images_task,
    resize_group_images_task,
)
from ..models import db
from ..models.event import Event, get_new_event_identifier
from ..models.group import Group
from ..models.speaker import Speaker
from ..models.exhibitor import Exhibitor
from tests.all.integration.auth_helper import create_super_admin

from .populate_db import populate
from .create_db import create_default_user
from .drop_db import db_drop_everything

logger = logging.getLogger(__name__)


@app.cli.command("list_routes")
def list_routes():
    import urllib

    output = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        line = urllib.parse.unquote(f"{rule.endpoint:50s} {methods:20s} {rule}")
        output.append(line)
    for line in sorted(output):
        print(line)


@app.cli.command('add_event_identifier')
def add_event_identifier():
    events = Event.query.all()
    for event in events:
        event.identifier = get_new_event_identifier()
        save_to_db(event)


@app.cli.command('fix_exhibitor_images')
def fix_exhibitor_images():
    exhibitors = Exhibitor.query.filter(
        Exhibitor.banner_url.isnot(None),
        Exhibitor.thumbnail_image_url == None  # noqa: E711
    ).all()
    print(f'Resizing images of { len(exhibitors) } exhibitors...')
    for exhibitor in exhibitors:
        print(f'Resizing Exhibitor { exhibitor.id }')
        resize_exhibitor_images_task.delay(exhibitor.id, exhibitor.banner_url)


@app.cli.command('fix_group_images')
def fix_group_images():
    groups = Group.query.filter(
        Group.banner_url.isnot(None), Group.thumbnail_image_url == None
    ).all()
    print(f'Resizing images of { len(groups) } groups...')
    for group in groups:
        print(f'Resizing image of Group { group.id } ')
        resize_group_images_task.delay(group.id, group.banner_url)


@app.cli.command('fix_event_and_speaker_images')
def fix_event_and_speaker_images():
    events = Event.query.filter(
        Event.original_image_url.isnot(None),
        or_(
            Event.thumbnail_image_url == None,  # noqa: E711
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
            Speaker.icon_image_url == None,  # noqa: E711
            Speaker.small_image_url == None,
            Speaker.thumbnail_image_url == None,
        ),
    ).all()

    logger.info('Resizing images of %s speakers...', len(speakers))
    for speaker in speakers:
        logging.info('Resizing Speaker %s', speaker.id)
        resize_speaker_images_task.delay(speaker.id, speaker.photo_url)


@app.cli.command('fix_digit_identifier')
def fix_digit_identifier():
    events = Event.query.filter(Event.identifier.op('~')(r'^[0-9\.]+$')).all()
    for event in events:
        event.identifier = get_new_event_identifier()
        db.session.add(event)
    db.session.commit()


@app.cli.command('initialize_db')
@click.option(
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
                    "[LOG] Could not create tables. "
                    "Either database does not exist or tables already created"
                )
            if populate_data:
                credentials = credentials.split(":")
                admin_email = os.environ.get('SUPER_ADMIN_EMAIL', credentials[0])
                admin_password = os.environ.get('SUPER_ADMIN_PASSWORD', credentials[1])
                create_super_admin(admin_email, admin_password)
                populate()
        else:
            print("[LOG] Tables already exist. Skipping data population & creation.")


@app.cli.command('prepare_db')
@click.pass_context
@with_appcontext
def prepare_db(ctx, credentials='open_event_test_user@fossasia.org:fossasia'):
    with app.app_context():
        ctx.invoke(initialize_db, credentials=credentials)


@app.cli.command('drop_db')
def drop_db():
    with app.app_context():
        db_drop_everything(db)


@app.cli.command('create_db')
def create_db():
    parser = argparse.ArgumentParser()
    parser.add_argument("email", nargs='?', help="The email for super_admin.", default='')
    parser.add_argument(
        "password", nargs='?', help="The password for super_admin.", default=''
    )
    parsed = parser.parse_args()
    with app.app_context():
        db.create_all()
        stamp()
        create_default_user(parsed.email, parsed.password)
        populate()


if __name__ == '__main__':
    prepare_db()

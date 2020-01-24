import logging
import os

from flask_migrate import MigrateCommand, stamp
from flask_script import Manager
from sqlalchemy import or_
from sqlalchemy.engine import reflection

from app.api.helpers.db import save_to_db
from app.instance import current_app as app
from app.api.helpers.tasks import resize_event_images_task, resize_speaker_images_task
from app.models import db
from app.models.event import Event, get_new_event_identifier
from app.models.module import Module
from app.models.speaker import Speaker
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
        line = urllib.parse.unquote(
            "{:50s} {:20s} {}".format(rule.endpoint, methods, rule)
        )
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
    events = Event.query.filter(Event.identifier.op('~')('^[0-9\.]+$')).all()
    for event in events:
        event.identifier = get_new_event_identifier()
        db.session.add(event)
    db.session.commit()


@manager.option('-n', '--name', dest='name', default='all')
@manager.option('-s', '--switch', dest='switch', default='off')
def module(name, switch):
    keys = [i.name for i in Module.__table__.columns][1:]
    convey = {"on": True, "off": False}
    if switch not in ['on', 'off']:
        print("Choose either state On/Off")

    elif name == 'all':
        for key in keys:
            setattr(Module.query.first(), key, convey[switch])
            print("Module %s turned %s" % (key, switch))
    elif name in keys:
        setattr(Module.query.first(), name, convey[switch])
        print("Module %s turned %s" % (name, switch))
    else:
        print("Invalid module selected")
    db.session.commit()


@manager.option('-e', '--event', help='Event ID. Eg. 1')
def fix_speaker_images(event):
    from app.helpers.sessions_speakers.speakers import speaker_image_sizes
    from app.helpers.sessions_speakers.speakers import save_resized_photo
    import urllib
    from app.helpers.storage import generate_hash

    event_id = int(event)
    image_sizes = speaker_image_sizes()
    speakers = Speaker.query.filter_by(event_id=event_id).all()
    for speaker in speakers:
        if speaker.photo and speaker.photo.strip() != '':
            file_relative_path = (
                'static/media/temp/' + generate_hash(str(speaker.id)) + '.jpg'
            )
            file_path = app.config['BASE_DIR'] + '/' + file_relative_path
            urllib.urlretrieve(speaker.photo, file_path)
            speaker.small = save_resized_photo(
                file_path, event_id, speaker.id, 'small', image_sizes
            )
            speaker.thumbnail = save_resized_photo(
                file_path, event_id, speaker.id, 'thumbnail', image_sizes
            )
            speaker.icon = save_resized_photo(
                file_path, event_id, speaker.id, 'icon', image_sizes
            )
            db.session.add(speaker)
            os.remove(file_path)
            print("Downloaded " + speaker.photo + " into " + file_relative_path)
        print("Processed - " + str(speaker.id))
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
def prepare_kubernetes_db(credentials='open_event_test_user@fossasia.org:fossasia'):
    with app.app_context():
        initialize_db(credentials)


if __name__ == "__main__":
    manager.run()

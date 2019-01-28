import os

from app.api.helpers.db import save_to_db
from app.models.event import Event, get_new_event_identifier
from app import manager
from app import current_app as app
from app.models import db
from app.models.speaker import Speaker
from populate_db import populate
from flask_migrate import stamp
from sqlalchemy.engine import reflection

from tests.all.integration.auth_helper import create_super_admin


@manager.command
def list_routes():
    import urllib

    output = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        line = urllib.unquote("{:50s} {:20s} {}".format(
            rule.endpoint, methods, rule))
        output.append(line)

    for line in sorted(output):
        print(line)


@manager.command
def add_event_identifier():
    events = Event.query.all()
    for event in events:
        event.identifier = get_new_event_identifier()
        save_to_db(event)


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
            file_relative_path = 'static/media/temp/' + generate_hash(str(speaker.id)) + '.jpg'
            file_path = app.config['BASE_DIR'] + '/' + file_relative_path
            urllib.urlretrieve(speaker.photo, file_path)
            speaker.small = save_resized_photo(file_path, event_id, speaker.id, 'small', image_sizes)
            speaker.thumbnail = save_resized_photo(file_path, event_id, speaker.id, 'thumbnail', image_sizes)
            speaker.icon = save_resized_photo(file_path, event_id, speaker.id, 'icon', image_sizes)
            db.session.add(speaker)
            os.remove(file_path)
            print("Downloaded " + speaker.photo + " into " + file_relative_path)
        print("Processed - " + str(speaker.id))
    db.session.commit()


@manager.option('-c', '--credentials', help='Super admin credentials. Eg. username:password')
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
                print("[LOG] Could not create tables. Either database does not exist or tables already created")
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

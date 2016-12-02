from app.helpers.data import save_to_db
from app.models.event import Event, get_new_event_identifier
from app import manager
from app import current_app as app
from app.models import db
from app.helpers.data import DataManager
from populate_db import populate
from flask.ext.migrate import stamp
from sqlalchemy.engine import reflection


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
        print line


@manager.command
def add_event_identifier():
    events = Event.query.all()
    for event in events:
        event.identifier = get_new_event_identifier()
        save_to_db(event)


@manager.option('-c', '--credentials', help='Super admin credentials. Eg. username:password')
def initialize_db(credentials):
    with app.app_context():
        populate_data = True
        inspector = reflection.Inspector.from_engine(db.engine)
        table_name = 'events'
        table_names = inspector.get_table_names()
        if table_name not in table_names:
            try:
                db.create_all()
                stamp()
            except:
                populate_data = False
                print "Could not create tables. Either database does not exist or tables already created"
            if populate_data:
                credentials = credentials.split(":")
                DataManager.create_super_admin(credentials[0], credentials[1])
                populate()


if __name__ == "__main__":
    manager.run()

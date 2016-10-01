"""Copyright 2015 Rafal Kowalski"""
from app.helpers.data import save_to_db
from app.models.event import Event, get_new_event_identifier
from app import manager
from app import current_app as app
from app.models import db
from app.helpers.data import DataManager
from populate_db import populate

@manager.command
def list_routes():
    import urllib.request, urllib.parse, urllib.error

    output = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        line = urllib.parse.unquote("{:50s} {:20s} {}".format(
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

@manager.option('-c', '--credentials', help='Super admin credentials. Eg. username:password')
def initialize_db(credentials):
    with app.app_context():
        db.create_all()
        credentials = credentials.split(":")
        DataManager.create_super_admin(credentials[0], credentials[1])
        populate()

if __name__ == "__main__":
    manager.run()

"""Copyright 2015 Rafal Kowalski"""
from app.helpers.data import save_to_db
from app.models.event import Event, get_new_event_identifier
from app import manager
from app import current_app as app


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

if __name__ == "__main__":
    manager.run()

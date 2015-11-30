"""Copyright 2015 Rafal Kowalski"""
from flask import url_for

from open_event import manager
from open_event import current_app as app

@manager.command
def list_routes():
    import urllib

    output = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        line = urllib.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, rule))
        output.append(line)

    for line in sorted(output):
        print line

if __name__ == "__main__":
    manager.run()

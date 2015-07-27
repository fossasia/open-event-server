"""Copyright 2015 Rafal Kowalski"""
from open_event import current_app
from open_event.models import db

if __name__ == "__main__":
    with current_app.app_context():
        db.create_all()
    current_app.run(host='0.0.0.0', debug=True)
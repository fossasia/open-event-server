"""Copyright 2015 Rafal Kowalski"""

if __name__ == "__main__":
    from open_event import current_app
    from open_event.models import db
    with current_app.app_context():
        db.create_all()
    current_app.run(host='0.0.0.0', debug=True)
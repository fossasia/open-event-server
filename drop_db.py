from open_event import current_app
from open_event.models import db

if __name__ == "__main__":
    with current_app.app_context():
        db.drop_all()

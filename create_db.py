from open_event import current_app
from open_event.models import db
from open_event.helpers.data import DataManager


def create_default_user():
    print "Your login is 'super_admin'"
    password = raw_input("Please enter password of Super Admin user")
    DataManager.create_super_admin(password)


if __name__ == "__main__":
    with current_app.app_context():
        db.create_all()
        create_default_user()


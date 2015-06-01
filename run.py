"""Written by - Rafal Kowalski"""
from open_event import app
from open_event.models import db

if __name__ == "__main__":
    # with app.app_context():
    #     db.create_all()
    app.run(debug=True)
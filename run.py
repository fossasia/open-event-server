from open_event import app
from open_event.models import db

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        # from open_event.models import Sponsor
        # x = Sponsor("test", "test@gmail.com", "aaa")
        # db.session.add(x)
        # db.session.commit()
        # print Sponsor.query.all()
        app.run(debug=True)
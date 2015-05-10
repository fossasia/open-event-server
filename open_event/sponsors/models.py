from open_event import db

class Sponsor(db.Model):
    __tablename__ = 'sponsors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    url = db.Column(db.String)
    logo = db.Column(db.String)

    def __init__(self, name=None, url=None, logo=None, ):
        self.name = name
        self.url = url
        self.logo = logo

    def __repr__(self):
        return '<Sponsor %r>' % (self.name)
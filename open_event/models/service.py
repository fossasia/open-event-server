from . import db


class Service(db.Model):
    __tablename__ = 'service'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)


    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Service %r>' % self.name

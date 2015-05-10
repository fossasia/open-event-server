from open_event import db

class Speaker(db.Model):
    __tablename__ = 'speakers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)

    def __init__(self, name=None):
        self.name = name

    def __repr__(self):
        return '<Speaker %r>' % (self.name)
from . import db


class Track(db.Model):
    __tablename__ = 'tracks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=False)
    session = db.relationship("Session")
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))

    def __init__(self, name=None, description=None, event_id=None):
        self.name = name
        self.description = description
        self.event_id = event_id

    def __repr__(self):
        return '<Track %r>' % (self.name)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'name': self.name,
                'description': self.description,
                }

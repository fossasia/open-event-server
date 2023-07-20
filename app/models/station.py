from app.models import db


class Station(db.Model):
    """Station database model"""

    id = db.Column(db.Integer, primary_key=True)
    station_name = db.Column(db.String, nullable=False)
    station_type = db.Column(db.String, nullable=True)
    microlocation_id = db.Column(
        db.Integer, db.ForeignKey('microlocations.id', ondelete='CASCADE')
    )
    microlocation = db.relationship(
        'Microlocation', backref='stations', foreign_keys=[microlocation_id]
    )
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    event = db.relationship('Event', backref='stations', foreign_keys=[event_id])

    def __repr__(self):
        return f'<Station {self.id}>'

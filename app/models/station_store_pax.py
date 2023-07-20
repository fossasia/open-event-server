from datetime import datetime

from app.models import db


class StationStorePax(db.Model):
    """Station Store Pax database model"""

    __tablename__ = 'station_store_paxs'
    id = db.Column(db.Integer, primary_key=True)
    station_id = db.Column(db.Integer, db.ForeignKey('station.id', ondelete='CASCADE'))
    station = db.relationship(
        'Station', backref='station_store_paxs', foreign_keys=[station_id]
    )
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id', ondelete='CASCADE'))
    session = db.relationship(
        'Session', backref='station_store_paxs', foreign_keys=[session_id]
    )
    current_pax = db.Column(db.Integer, default=0)
    created_at: datetime = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    modified_at: datetime = db.Column(
        db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f'<StationStorePax {self.id}>'

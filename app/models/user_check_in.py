import datetime

from sqlalchemy import ARRAY, Integer, func

from app.models import db
from app.models.base import SoftDeletionModel


class UserCheckIn(db.Model):
    """User check in database model"""

    id = db.Column(db.Integer, primary_key=True)

    ticket_holder_id = db.Column(
        db.Integer, db.ForeignKey('ticket_holders.id', ondelete='CASCADE')
    )
    ticket_holder = db.relationship(
        'TicketHolder', backref='user_check_ins', foreign_keys=[ticket_holder_id]
    )

    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id', ondelete='CASCADE'))
    session = db.relationship(
        'Session', backref='user_check_ins', foreign_keys=[session_id]
    )

    station_id = db.Column(db.Integer, db.ForeignKey('station.id', ondelete='CASCADE'))
    station = db.relationship(
        'Station', backref='user_check_ins', foreign_keys=[station_id]
    )

    track_name = db.Column(db.String, nullable=True)
    session_name = db.Column(db.String, nullable=True)
    speaker_name = db.Column(db.String, nullable=True)
    check_in_out_at = db.Column(db.DateTime(timezone=True))
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow())
    updated_at = db.Column(db.DateTime(timezone=True))
    is_deleted = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<User Check In {self.id}>'


class VirtualCheckIn(SoftDeletionModel):
    """Virtual check in database model"""

    __tablename__ = 'virtual_check_in'

    id = db.Column(db.Integer, primary_key=True)

    ticket_holder_id = db.Column(ARRAY(Integer), nullable=True)

    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='SET NULL'))
    event = db.relationship('Event', backref='virtual_check_ins')

    microlocation_id = db.Column(
        db.Integer,
        db.ForeignKey('microlocations.id', ondelete='SET NULL'),
        nullable=True,
        default=None,
    )
    microlocation = db.relationship('Microlocation', backref='virtual_check_ins')

    check_in_type = db.Column(db.String, nullable=False)
    check_in_at = db.Column(db.DateTime(timezone=True))
    check_out_at = db.Column(db.DateTime(timezone=True))

    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True))
    is_deleted = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Virtual Check In {self.id}>'

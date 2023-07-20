from sqlalchemy.sql import func as sql_func

from app.models import db


class UserCheckIn(db.Model):
    """User check in database model"""

    id = db.Column(db.Integer, primary_key=True)

    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id', ondelete='CASCADE'))
    ticket = db.relationship('Ticket', backref='user_check_ins', foreign_keys=[ticket_id])

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
    created_at = db.Column(db.DateTime(timezone=True), default=sql_func.now())
    updated_at = db.Column(db.DateTime(timezone=True))
    is_deleted = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<User Check In {self.id}>'

from app.models import db


class CustomFormTickets(db.Model):
    """Custom Form Ticket model class"""
    __tablename__ = 'custom_form_ticket'
    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.String, nullable=False)
    ticket_id: int = db.Column(
        db.Integer, db.ForeignKey('tickets.id', ondelete='CASCADE')
    )
    ticket = db.relationship('Ticket', backref='custom_form_ticket', foreign_keys=[ticket_id])
    event_id: int = db.Column(
        db.Integer, db.ForeignKey('events.id', ondelete='CASCADE')
    )
    event = db.relationship('Event', backref='custom_form_ticket', foreign_keys=[event_id])

    def __repr__(self):
        return '<CustomFormTicket %r>' % self.id

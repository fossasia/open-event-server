from app.models import db


class CustomFormTickets(db.Model):
    """Custom Form Ticket model class"""
    __tablename__ = 'custom_form_ticket'
    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.String, nullable=False)
    ticket_id = db.Column(
        db.Integer, db.ForeignKey('tickets.id', ondelete='CASCADE')
    )

    def __repr__(self):
        return '<CustomFormTicket %r>' % self.id

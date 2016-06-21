from . import db


class Ticket(db.Model):
    __tablename__ = 'ticket'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    description = db.Column(db.String)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer)

    event_id = db.Column(
        db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    event = db.relationship('Event', backref='tickets')

    def __init__(self, name, quantity, event, description=None, price=0):
        self.name = name
        self.quantity = quantity
        self.event = event
        self.description = description
        self.price = price

    def __repr__(self):
        return '<Ticket %r>' % self.name


class BookedTicket(db.Model):
    __tablename__ = 'booked_ticket'
    __table_args__ = (db.UniqueConstraint('user_id',
                                          'ticket_id',
                                          name='user_ticket_uc'), )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='booked_tickets')
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'))
    ticket = db.relationship('Ticket', backref='booked_tickets')
    quantity = db.Column(db.Integer)

    def __init__(self, user, ticket, quantity):
        self.user = user
        self.ticket = ticket
        self.quantity = quantity

    def __repr__(self):
        return '<BookedTicket {}:{}'.format(self.user, self.ticket)

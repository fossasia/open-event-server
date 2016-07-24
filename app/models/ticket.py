from . import db


class Ticket(db.Model):
    __tablename__ = 'ticket'
    __table_args__ = (db.UniqueConstraint('name',
                                          'event_id',
                                          name='name_event_uc'), )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    type = db.Column(db.String)
    quantity = db.Column(db.Integer)
    price = db.Column(db.Integer)

    sales_start = db.Column(db.DateTime)
    sales_end = db.Column(db.DateTime)

    min_order = db.Column(db.Integer)
    max_order = db.Column(db.Integer)

    event_id = db.Column(
        db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    event = db.relationship('Event', backref='tickets')

    def __init__(self,
                 name,
                 type,
                 sales_start,
                 sales_end,
                 description=None,
                 event=None,
                 quantity=100,
                 price=0,
                 min_order=1,
                 max_order=10):
        self.name = name
        self.quantity = quantity
        self.type = type
        self.event = event
        self.description = description
        self.price = price
        self.sales_start = sales_start
        self.sales_end = sales_end
        self.min_order = min_order
        self.max_order = max_order

    def __repr__(self):
        return '<Ticket %r>' % self.name

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.name


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
        return '<BookedTicket %r by %r' % (self.ticket,
                                           self.user, )

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.ticket

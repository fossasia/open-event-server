from . import db


ticket_tags_table = db.Table('association', db.Model.metadata,
    db.Column('ticket_id', db.Integer, db.ForeignKey('ticket.id')),
    db.Column('ticket_tag_id', db.Integer, db.ForeignKey('ticket_tag.id'))
)


class Ticket(db.Model):
    __tablename__ = 'ticket'
    __table_args__ = (db.UniqueConstraint('name',
                                          'event_id',
                                          name='name_event_uc'), )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    description_toggle = db.Column(db.Boolean)
    type = db.Column(db.String)
    quantity = db.Column(db.Integer)
    price = db.Column(db.Integer)

    sales_start = db.Column(db.DateTime)
    sales_end = db.Column(db.DateTime)
    hide = db.Column(db.Boolean)

    min_order = db.Column(db.Integer)
    max_order = db.Column(db.Integer)

    event_id = db.Column(
        db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    event = db.relationship('Event', backref='tickets')

    tags = db.relationship('TicketTag', secondary=ticket_tags_table, backref='tickets')

    def __init__(self,
                 name,
                 event=None,
                 type=None,
                 sales_start=None,
                 sales_end=None,
                 hide=False,
                 description=None,
                 description_toggle=True,
                 quantity=100,
                 price=0,
                 min_order=1,
                 max_order=10,
                 tags=[]):
        self.name = name
        self.quantity = quantity
        self.type = type
        self.event = event
        self.description = description
        self.description_toggle = description_toggle
        self.price = price
        self.sales_start = sales_start
        self.sales_end = sales_end
        self.hide = hide
        self.min_order = min_order
        self.max_order = max_order
        self.tags = tags

    def has_order_tickets(self):
        """Returns True if ticket has already placed orders.
        Else False.
        """
        return bool(len(self.order_tickets) > 0)

    def tags_csv(self):
        """Return list of Tags in CSV.
        """
        tag_names = [tag.name for tag in self.tags]
        return ','.join(tag_names)

    def __repr__(self):
        return '<Ticket %r>' % self.name

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.name


class TicketTag(db.Model):
    """Tags to group tickets
    """
    __tablename__ = 'ticket_tag'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    event = db.relationship('Event', backref='ticket_tags')

    def __init__(self, name, event_id):
        self.name = name
        self.event_id = event_id

    def __repr__(self):
        return '<TicketTag %r>' % self.name

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

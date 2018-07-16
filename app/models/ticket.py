from app.models import db
from app.models.base import SoftDeletionModel
from app.models.order import OrderTicket, Order

access_codes_tickets = db.Table('access_codes_tickets',
                                db.Column('access_code_id', db.Integer, db.ForeignKey(
                                    'access_codes.id', ondelete='CASCADE')),
                                db.Column('ticket_id', db.Integer, db.ForeignKey('tickets.id', ondelete='CASCADE')),
                                db.PrimaryKeyConstraint('access_code_id', 'ticket_id'))

discount_codes_tickets = db.Table(
    'discount_codes_tickets',
    db.Column('discount_code_id', db.Integer, db.ForeignKey('discount_codes.id', ondelete='CASCADE')),
    db.Column('ticket_id', db.Integer, db.ForeignKey('tickets.id', ondelete='CASCADE')),
    db.PrimaryKeyConstraint('discount_code_id', 'ticket_id'))

ticket_tags_table = db.Table('association', db.Model.metadata,
                             db.Column('ticket_id', db.Integer, db.ForeignKey('tickets.id', ondelete='CASCADE')),
                             db.Column('ticket_tag_id', db.Integer, db.ForeignKey('ticket_tag.id', ondelete='CASCADE'))
                             )


class Ticket(SoftDeletionModel):
    __tablename__ = 'tickets'
    __table_args__ = (db.UniqueConstraint('name', 'event_id', name='name_event_uc'),)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    is_description_visible = db.Column(db.Boolean)
    type = db.Column(db.String, nullable=False)
    quantity = db.Column(db.Integer)
    position = db.Column(db.Integer)
    price = db.Column(db.Float)
    is_fee_absorbed = db.Column(db.Boolean)
    sales_starts_at = db.Column(db.DateTime(timezone=True), nullable=False)
    sales_ends_at = db.Column(db.DateTime(timezone=True), nullable=False)
    is_hidden = db.Column(db.Boolean)

    min_order = db.Column(db.Integer)
    max_order = db.Column(db.Integer)
    is_checkin_restricted = db.Column(db.Boolean)
    auto_checkin_enabled = db.Column(db.Boolean)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    event = db.relationship('Event', backref='tickets_')

    tags = db.relationship('TicketTag', secondary=ticket_tags_table, backref='tickets')
    order_ticket = db.relationship('OrderTicket', backref="ticket", passive_deletes=True)

    access_codes = db.relationship('AccessCode', secondary=access_codes_tickets, backref='tickets')

    discount_codes = db.relationship('DiscountCode', secondary=discount_codes_tickets, backref="tickets")

    def __init__(self,
                 name=None,
                 event_id=None,
                 type=None,
                 sales_starts_at=None,
                 sales_ends_at=None,
                 is_hidden=False,
                 description=None,
                 is_description_visible=True,
                 is_checkin_restricted=True,
                 auto_checkin_enabled=False,
                 quantity=100,
                 position=1,
                 price=0,
                 min_order=1,
                 max_order=10,
                 is_fee_absorbed=False,
                 tags=[],
                 access_codes=[],
                 discount_codes=[]):

        self.name = name
        self.quantity = quantity
        self.position = position
        self.type = type
        self.event_id = event_id
        self.description = description
        self.is_description_visible = is_description_visible
        self.is_checkin_restricted = is_checkin_restricted
        self.auto_checkin_enabled = auto_checkin_enabled
        self.price = price
        self.sales_starts_at = sales_starts_at
        self.sales_ends_at = sales_ends_at
        self.is_hidden = is_hidden
        self.min_order = min_order
        self.max_order = max_order
        self.tags = tags
        self.is_fee_absorbed = is_fee_absorbed
        self.access_codes = access_codes
        self.discount_codes = discount_codes

    def has_order_tickets(self):
        """Returns True if ticket has already placed orders.
        Else False.
        """
        from app.api.helpers.db import get_count
        orders = Order.id.in_(OrderTicket.query.with_entities(OrderTicket.order_id).filter_by(ticket_id=self.id).all())
        count = get_count(Order.query.filter(orders).filter(Order.status != 'deleted'))
        # Count is zero if no completed orders are present
        return bool(count > 0)

    def has_completed_order_tickets(self):
        """Returns True if ticket has already placed orders.
        Else False.
        """
        order_tickets = OrderTicket.query.filter_by(ticket_id=self.id)

        count = 0
        for order_ticket in order_tickets:
            order = Order.query.filter_by(id=order_ticket.order_id).first()
            if order.status == "completed" or order.status == "placed":
                count += 1

        return bool(count > 0)

    def tags_csv(self):
        """Return list of Tags in CSV.
        """
        tag_names = [tag.name for tag in self.tags]
        return ','.join(tag_names)

    def __repr__(self):
        return '<Ticket %r>' % self.name

    def __str__(self):
        return self.__repr__()

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        data = {
            'id': self.id,
            'name': self.name,
            'quantity': self.quantity,
            'position': self.position,
            'type': self.type,
            'description_visibility': self.is_description_visible,
            'description': self.description,
            'price': self.price,
            'sales_start_date': self.sales_starts_at.strftime('%m/%d/%Y') if self.sales_starts_at else '',
            'sales_starts_at': self.sales_starts_at.strftime('%H:%M') if self.sales_starts_at else '',
            'sales_end_date': self.sales_ends_at.strftime('%m/%d/%Y') if self.sales_ends_at else '',
            'sales_ends_at': self.sales_ends_at.strftime('%H:%M') if self.sales_ends_at else '',
            'ticket_visibility': self.hide,
            'min_order': self.min_order,
            'max_order': self.max_order,
            'tags_string': '',
            'has_orders': self.has_order_tickets(),
            'has_completed_orders': self.has_completed_order_tickets(),
            'is_fee_absorbed': self.is_fee_absorbed
        }

        tags = []
        for tag in self.tags:
            tags.append(tag.name)

        data['tags'] = ",".join(tags)
        return data


class TicketTag(SoftDeletionModel):
    """
    Tags to group tickets
    """
    __tablename__ = 'ticket_tag'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    event = db.relationship('Event', backref='ticket_tags')

    def __init__(self, name=None, event_id=None, deleted_at=None):
        self.name = name
        self.event_id = event_id
        self.deleted_at = deleted_at

    def __repr__(self):
        return '<TicketTag %r>' % self.name

    def __str__(self):
        return self.__repr__()

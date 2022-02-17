from sqlalchemy import or_

from app.api.helpers.errors import ConflictError
from app.models import db
from app.models.base import SoftDeletionModel
from app.models.order import Order, OrderTicket
from app.models.ticket_holder import TicketHolder

access_codes_tickets = db.Table(
    'access_codes_tickets',
    db.Column(
        'access_code_id', db.Integer, db.ForeignKey('access_codes.id', ondelete='CASCADE')
    ),
    db.Column('ticket_id', db.Integer, db.ForeignKey('tickets.id', ondelete='CASCADE')),
    db.PrimaryKeyConstraint('access_code_id', 'ticket_id'),
)

discount_codes_tickets = db.Table(
    'discount_codes_tickets',
    db.Column(
        'discount_code_id',
        db.Integer,
        db.ForeignKey('discount_codes.id', ondelete='CASCADE'),
    ),
    db.Column('ticket_id', db.Integer, db.ForeignKey('tickets.id', ondelete='CASCADE')),
    db.PrimaryKeyConstraint('discount_code_id', 'ticket_id'),
)

ticket_tags_table = db.Table(
    'ticket_tagging',
    db.Model.metadata,
    db.Column('ticket_id', db.Integer, db.ForeignKey('tickets.id', ondelete='CASCADE')),
    db.Column(
        'ticket_tag_id', db.Integer, db.ForeignKey('ticket_tag.id', ondelete='CASCADE')
    ),
)


class Ticket(SoftDeletionModel):
    __tablename__ = 'tickets'
    __table_args__ = (
        db.UniqueConstraint(
            'name', 'event_id', 'deleted_at', name='name_event_deleted_at_uc'
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    is_description_visible = db.Column(db.Boolean)
    type = db.Column(db.String, nullable=False)
    quantity = db.Column(db.Integer, default=100)
    position = db.Column(db.Integer, default=1)
    price = db.Column(db.Float)
    min_price = db.Column(db.Float, default=0, nullable=False)
    max_price = db.Column(db.Float, default=0)
    is_fee_absorbed = db.Column(db.Boolean, default=False)
    sales_starts_at = db.Column(db.DateTime(timezone=True), nullable=False)
    sales_ends_at = db.Column(db.DateTime(timezone=True), nullable=False)
    is_hidden = db.Column(db.Boolean, default=False)

    min_order = db.Column(db.Integer, default=1)
    max_order = db.Column(db.Integer, default=10)
    is_checkin_restricted = db.Column(db.Boolean)
    auto_checkin_enabled = db.Column(db.Boolean, default=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    event = db.relationship('Event', backref='tickets_')

    tags = db.relationship('TicketTag', secondary=ticket_tags_table, backref='tickets')
    order_ticket = db.relationship('OrderTicket', backref="ticket", passive_deletes=True)

    access_codes = db.relationship(
        'AccessCode', secondary=access_codes_tickets, backref='tickets'
    )

    discount_codes = db.relationship(
        'DiscountCode', secondary=discount_codes_tickets, backref="tickets"
    )

    def has_order_tickets(self):
        """Returns True if ticket has already placed orders.
        Else False.
        """
        from app.api.helpers.db import get_count

        orders = Order.id.in_(
            OrderTicket.query.with_entities(OrderTicket.order_id)
            .filter_by(ticket_id=self.id)
            .all()
        )
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
        """Return list of Tags in CSV."""
        tag_names = [tag.name for tag in self.tags]
        return ','.join(tag_names)

    @property
    def has_current_orders(self):
        return db.session.query(
            Order.query.join(TicketHolder)
            .filter(
                TicketHolder.ticket_id == self.id,
                or_(
                    Order.status == 'completed',
                    Order.status == 'placed',
                    Order.status == 'pending',
                    Order.status == 'initializing',
                ),
            )
            .exists()
        ).scalar()

    @property
    def reserved_count(self):
        from app.api.attendees import get_sold_and_reserved_tickets_count

        return get_sold_and_reserved_tickets_count(self.id)

    @property
    def is_available(self):
        return self.reserved_count < self.quantity

    def raise_if_unavailable(self):
        if not self.is_available:
            raise ConflictError({'id': self.id}, f'Ticket "{self.name}" already sold out')

    def __repr__(self):
        return '<Ticket %r>' % self.name


class TicketTag(SoftDeletionModel):
    """
    Tags to group tickets
    """

    __tablename__ = 'ticket_tag'
    __table_args__ = (db.UniqueConstraint('name', 'event_id', name='unique_ticket_tag'),)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    event = db.relationship('Event', backref='ticket_tags')

    def __repr__(self):
        return '<TicketTag %r>' % self.name

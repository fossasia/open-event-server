from . import db

class TicketHolder(db.Model):
    __tablename__ = "ticket_holders"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String)
    address = db.Column(db.String)
    city = db.Column(db.String)
    state = db.Column(db.String)
    country = db.Column(db.String)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    order = db.relationship('Order', backref='ticket_holders')

    def __init__(self,
                 name=None,
                 email=None,
                 address=None,
                 city=None,
                 state=None,
                 country=None,
                 order_id=None):
        self.name = name
        self.email = email
        self.city = city
        self.address = address
        self.state = state
        self.country = country
        self.order_id = order_id

    def __repr__(self):
        return '<Order %r>' % self.id

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.identifier

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {'id': self.id,
                'name': self.name,
                'email': self.email,
                'city': self.city,
                'address': self.address,
                'state': self.state,
                'country': self.country}

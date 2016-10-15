from . import db

class DiscountCode(db.Model):
    __tablename__ = "discount_codes"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String)
    value = db.Column(db.Integer)
    type = db.Column(db.String)
    is_active = db.Column(db.Boolean)
    tickets_number = db.Column(db.Integer)
    min_quantity = db.Column(db.Integer)
    max_quantity = db.Column(db.Integer)
    valid_from = db.Column(db.DateTime, nullable=True)
    valid_till = db.Column(db.DateTime, nullable=True)
    tickets = db.Column(db.String)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    event = db.relationship('Event', backref='discount_codes')

    marketer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    marketer = db.relationship('User', backref='discount_codes')

    def __init__(self,
                 code=None,
                 value=None,
                 type=None,
                 tickets_number=None,
                 min_quantity=None,
                 max_quantity=None,
                 valid_from=None,
                 valid_till=None,
                 is_active=True,
                 event_id=None):
        self.code = code
        self.type = type
        self.value = value
        self.tickets_number = tickets_number
        self.min_quantity = min_quantity
        self.max_quantity = max_quantity
        self.valid_from = valid_from
        self.valid_till = valid_till
        self.event_id = event_id
        self.is_active = is_active

    def __repr__(self):
        return '<DiscountCode %r>' % self.id

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.identifier

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {'id': self.id,
                'code': self.code,
                'value': self.value,
                'tickets_number': self.tickets_number,
                'event_id': self.event_id,
                'is_active': self.is_active}

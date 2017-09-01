from app.models import db


class FaqType(db.Model):
    """Page model class"""
    __tablename__ = 'faq_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    event_id = db.Column(db.Integer,
                         db.ForeignKey('events.id', ondelete='CASCADE'))
    event = db.relationship("Event", backref="faq_types", foreign_keys=[event_id])
    faqs = db.relationship('Faq', backref="faq_type")

    def __init__(self, name=None, event_id=None):
        self.name = name
        self.event_id = event_id

    def __repr__(self):
        return '<FAQType %r>' % self.name

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.name

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
        }

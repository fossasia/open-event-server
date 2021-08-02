from sqlalchemy.orm import backref

from app.models import db


class StripeAuthorization(db.Model):
    """
    Stripe authorization information for an event.
    """

    __tablename__ = 'stripe_authorizations'

    id = db.Column(db.Integer, primary_key=True)
    stripe_secret_key = db.Column(db.String)
    stripe_refresh_token = db.Column(db.String)
    stripe_publishable_key = db.Column(db.String)
    stripe_user_id = db.Column(db.String)
    stripe_auth_code = db.Column(db.String)

    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    event = db.relationship(
        'Event', backref=backref('stripe_authorization', uselist=False)
    )

    def __repr__(self):
        return '<StripeAuthorization %r>' % self.stripe_user_id

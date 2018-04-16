from __future__ import unicode_literals

from future.utils import python_2_unicode_compatible

from app.models import db
from utils.compat import u


@python_2_unicode_compatible
class Module(db.Model):
    """File model class"""
    __tablename__ = 'modules'
    id = db.Column(db.Integer,
                   primary_key=True)
    ticket_include = db.Column(db.Boolean, default=False)
    payment_include = db.Column(db.Boolean, default=False)
    donation_include = db.Column(db.Boolean, default=False)

    def __init__(self,
                 ticket_include=None,
                 payment_include=None,
                 donation_include=None):
        self.ticket_include = ticket_include
        self.payment_include = payment_include
        self.donation_include = donation_include

    def __repr__(self):
        return '<Module %r>' % self.id

    def __str__(self):
        return u('<Module %r' % self.id)

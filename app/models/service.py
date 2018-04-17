from __future__ import unicode_literals

from future.utils import python_2_unicode_compatible

from app.models import db
from utils.compat import u


@python_2_unicode_compatible
class Service(db.Model):
    __tablename__ = 'services'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Service %r>' % self.name

    def __str__(self):
        return u(self.name)

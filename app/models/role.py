from __future__ import unicode_literals

from future.utils import python_2_unicode_compatible

from app.models import db
from utils.compat import u


@python_2_unicode_compatible
class Role(db.Model):
    """Event Role
    """
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    title_name = db.Column(db.String)

    def __init__(self, name=None, title_name=None):
        self.name = name
        self.title_name = title_name

    def __repr__(self):
        return '<Role %r>' % self.name

    def __str__(self):
        return u(self.name)

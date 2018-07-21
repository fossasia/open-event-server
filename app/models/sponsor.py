from app.models import db
from app.models.base import SoftDeletionModel
from app.models.helpers.versioning import clean_up_string, clean_html


class Sponsor(SoftDeletionModel):
    """Sponsor model class"""
    __tablename__ = 'sponsors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    url = db.Column(db.String)
    level = db.Column(db.Integer)
    logo_url = db.Column(db.String)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    type = db.Column(db.String)

    def __init__(self, name=None, url=None, logo_url=None, event_id=None,
                 description=None, type=None, level=None, deleted_at=None):
        self.name = name
        self.url = url
        self.logo_url = logo_url
        self.event_id = event_id
        self.level = level
        self.type = type
        self.description = description
        self.deleted_at = deleted_at

    @staticmethod
    def get_service_name():
        return 'sponsor'

    def __repr__(self):
        return '<Sponsor %r>' % self.name

    def __str__(self):
        return self.__repr__()

    def __setattr__(self, name, value):
        if name == 'description':
            super(Sponsor, self).__setattr__(name, clean_html(clean_up_string(value)))
        else:
            super(Sponsor, self).__setattr__(name, value)

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'logo_url': self.logo_url,
            'level': self.level,
            'type': self.type,
            'description': self.description,
        }

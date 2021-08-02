from app.models import db
from app.models.base import SoftDeletionModel
from app.models.helpers.versioning import clean_html, clean_up_string


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

    @staticmethod
    def get_service_name():
        return 'sponsor'

    def __repr__(self):
        return '<Sponsor %r>' % self.name

    def __setattr__(self, name, value):
        if name == 'description':
            super().__setattr__(name, clean_html(clean_up_string(value)))
        else:
            super().__setattr__(name, value)

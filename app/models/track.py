from app.models import db
from app.models.base import SoftDeletionModel


class Track(SoftDeletionModel):
    """Track model class"""
    __tablename__ = 'tracks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String, nullable=False)
    sessions = db.relationship('Session', backref='track')
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))

    def __init__(self, name=None, description=None, event_id=None,
                 session=None, color=None, deleted_at=None):
        self.name = name
        self.description = description
        self.event_id = event_id
        self.session_id = session
        self.color = color
        self.deleted_at = deleted_at

    @staticmethod
    def get_service_name():
        return 'track'

    def __repr__(self):
        return '<Track %r>' % self.name

    def __str__(self):
        return self.__repr__()

    @property
    def font_color(self):
        if self.color.startswith('#'):
            h = self.color.lstrip('#')
            a = 1 - (0.299 * int(h[0:2], 16) + 0.587 * int(h[2:4], 16) + 0.114 * int(h[4:6], 16))/255
        elif self.color.startswith('rgba'):
            h = self.color.lstrip('rgba').replace('(', '', 1).replace(')', '', 1)
            h = h.split(',')
            a = 1 - (0.299 * int(int(h[0]), 16) + 0.587 * int(int(h[1]), 16) + 0.114 * int(int(h[2]), 16)) / 255
        return '#000000' if (a < 0.5) else '#ffffff'

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'font_color': self.font_color
        }

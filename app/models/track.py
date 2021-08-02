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

    @staticmethod
    def get_service_name():
        return 'track'

    def __repr__(self):
        return '<Track %r>' % self.name

    @property
    def font_color(self):
        if self.color.startswith('#'):
            h = self.color.lstrip('#')
            a = (
                1
                - (
                    0.299 * int(h[0:2], 16)
                    + 0.587 * int(h[2:4], 16)
                    + 0.114 * int(h[4:6], 16)
                )
                / 255
            )
        elif self.color.startswith('rgba'):
            h = self.color.lstrip('rgba').replace('(', '', 1).replace(')', '', 1)
            h = h.split(',')
            a = (
                1
                - (0.299 * int(h[0], 16) + 0.587 * int(h[1], 16) + 0.114 * int(h[2], 16))
                / 255
            )
        return '#000000' if (a < 0.5) else '#ffffff'

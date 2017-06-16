from app.models import db


class Track(db.Model):
    """Track model class"""
    __tablename__ = 'tracks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String, nullable=False)
    sessions = db.relationship('Session', backref='track')
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))

    def __init__(self, name=None, description=None, event_id=None,
                 session=None, color=None):
        self.name = name
        self.description = description
        self.event_id = event_id
        self.session_id = session
        self.color = color

    @staticmethod
    def get_service_name():
        return 'track'

    def __repr__(self):
        return '<Track %r>' % self.name

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.name

    @property
    def font_color(self):
        h = self.color.lstrip('#')
        a = 1 - (0.299 * int(h[0:2], 16) + 0.587 * int(h[2:4], 16) + 0.114 * int(h[4:6], 16))/255
        return '#000000' if (a < 0.5) else '#ffffff'

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'font_color': self.font_color
        }

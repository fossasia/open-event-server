from app.models import db


class SocialLink(db.Model):
    __tablename__ = "social_links"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    link = db.Column(db.String, nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    event = db.relationship("Event", backref="social_link")

    def __init__(self, name=None, link=None, event_id=None):
        self.name = name
        self.link = link
        self.event_id = event_id

    def __repr__(self):
        return '<SocialLink %r>' % self.name

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.name

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id, 'name': self.name, 'link': self.link}

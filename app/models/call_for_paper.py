from sqlalchemy.orm import backref

from app.models import db


class CallForPaper(db.Model):
    """call for paper model class"""
    __tablename__ = 'call_for_papers'
    id = db.Column(db.Integer, primary_key=True)
    announcement = db.Column(db.Text, nullable=False)
    starts_at = db.Column(db.DateTime(timezone=True), nullable=False)
    ends_at = db.Column(db.DateTime(timezone=True), nullable=False)
    hash = db.Column(db.String, nullable=True)
    privacy = db.Column(db.String, nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    event = db.relationship("Event", backref=backref("call_for_papers", uselist=False))

    def __init__(self, announcement=None, starts_at=None, ends_at=None, hash=None, privacy='public',
                 event_id=None):
        self.announcement = announcement
        self.starts_at = starts_at
        self.ends_at = ends_at
        self.hash = hash
        self.privacy = privacy
        self.event_id = event_id

    def __repr__(self):
        return '<call_for_papers %r>' % self.announcement

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.announcement

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""

        return {
            'id': self.id,
            'announcement': self.announcement,
            'starts_at': self.starts_at.strftime('%m/%d/%Y') if self.starts_at else '',
            'starts_at': self.starts_at.strftime('%H:%M') if self.starts_at else '',
            'ends_at': self.ends_at.strftime('%m/%d/%Y') if self.ends_at else '',
            'ends_at': self.ends_at.strftime('%H:%M') if self.ends_at else '',
            'privacy': self.privacy,
            'hash': self.hash
        }

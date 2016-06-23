from . import db


class CustomForms(db.Model):
    """custom form model class"""
    __tablename__ = 'custom_forms'
    id = db.Column(db.Integer, primary_key=True)
    session_form = db.Column(db.String, nullable=False)
    speaker_form = db.Column(db.String, nullable=False)
    event_id = db.Column(
        db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    events = db.relationship("Event", backref="custom_forms")

    def __init__(self, event_id=None, session_form=None, speaker_form=None):
        self.event_id = event_id
        self.session_form = session_form
        self.speaker_form = speaker_form

    def __repr__(self):
        return '<CustomForm %r>' % self.id

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return 'CustomForm %r' % self.id

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""

        return {'id': self.id, 'session_form': self.session_form, 'speaker_form': self.speaker_form}

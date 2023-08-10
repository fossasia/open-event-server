from app.models import db
from app.models.base import SoftDeletionModel


class Tag(SoftDeletionModel):
    """Tag model class"""

    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    event = db.relationship("Event", backref="tags_", foreign_keys=[event_id])

    def __repr__(self):
        return '<Tag %r>' % self.id

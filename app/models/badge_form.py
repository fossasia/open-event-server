from app.models import db


class BadgeForms(db.Model):
    """Badge Form database model"""

    id = db.Column(db.Integer, primary_key=True)
    badge_id = db.Column(db.String, nullable=False)
    badge_size = db.Column(db.String, nullable=True)
    badge_color = db.Column(db.String, nullable=True)
    badge_image_url = db.Column(db.String, nullable=True)
    badge_orientation = db.Column(db.String, nullable=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    event = db.relationship('Event', backref='badge_forms_')

    def __repr__(self):
        return f'<BadgeForm {self.id}>'

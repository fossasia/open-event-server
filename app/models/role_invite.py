from datetime import datetime, timedelta

from app.models import db


class RoleInvite(db.Model):
    __tablename__ = 'role_invites'

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String)

    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    event = db.relationship('Event', back_populates='role_invites')

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'))
    role = db.relationship("Role")

    hash = db.Column(db.String)
    created_at = db.Column(db.DateTime(timezone=True))
    is_declined = db.Column(db.Boolean)

    def __init__(self, email, event, role, created_at, is_declined=False):
        self.email = email
        self.event = event
        self.role = role
        self.created_at = created_at
        self.is_declined = is_declined

    def has_expired(self):
        # Check if invitation link has expired (it expires after 24 hours)
        return datetime.now() > self.created_at + timedelta(hours=24)

    def __repr__(self):
        return '<RoleInvite %r:%r:%r>' % (self.email,
                                          self.event,
                                          self.role,)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return 'Invite for %r:%r:%r' % (self.email,
                                        self.event,
                                        self.role)

from . import db


class RoleInvite(db.Model):
    __tablename__ = 'role_invite'

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String)

    event_id = db.Column(
        db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    event = db.relationship('Event', back_populates='role_invites')

    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    role = db.relationship("Role")

    hash = db.Column(db.String)
    create_time = db.Column(db.DateTime)

    def __init__(self, email, event, role, create_time):
        self.email = email
        self.event = event
        self.role = role
        self.create_time = create_time

    def __repr__(self):
        return '<RoleInvite %r:%r:%r>' % (self.email,
                                          self.event,
                                          self.role, )

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return 'Invite for %r' % (self.email,
                                  self.event,
                                  self.role, )

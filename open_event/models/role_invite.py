from . import db


class RoleInvite(db.Model):
    __tablename__ = 'role_invite'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User')

    event_id = db.Column(
        db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    event = db.relationship('Event', back_populates='role_invites')

    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    role = db.relationship("Role")

    hash = db.Column(db.String)

    def __init__(self, user, event, role):
        self.user = user
        self.event = event
        self.role = role

    def __repr__(self):
        return '<RoleInvite %r:%r:%r>' % (self.user,
                                          self.event,
                                          self.role, )

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return 'Invite %r: %r for %r' % (self.user,
                                         self.event,
                                         self.role, )

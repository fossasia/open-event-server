from . import db


class Notification(db.Model):
    """
    Model for storing user notifications.
    """

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='notifications')

    title = db.Column(db.String)
    message = db.Column(db.Text)
    received_at = db.Column(db.DateTime)
    has_read = db.Column(db.Boolean)

    def __init__(self, user, title, message, received_at, has_read=False):
        self.user = user
        self.title = title
        self.message = message
        self.received_at = received_at
        self.has_read = has_read

    def __repr__(self):
        return '<Notif %s:%s>' % (self.user, self.title)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return '%r: %r' % (self.user, self.title)

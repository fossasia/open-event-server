from . import db


class Permission(db.Model):
    __tablename__ = 'permissions'
    __table_args__ = (db.UniqueConstraint('user_id',
                                          'service',
                                          'service_id',
                                          name='user_service_uc'), )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User')
    service = db.Column(db.String, nullable=False)
    service_id = db.Column(db.Integer, nullable=False)
    modes = db.Column(db.Integer, nullable=False)

    def __init__(self, user=None, service=None, service_id=None, modes=None):
        self.user = user
        self.service = service
        self.service_id = service_id
        self.modes = modes

    def __repr__(self):
        return '<Perm %r for %r>' % (self.user,
                                     self.service, )

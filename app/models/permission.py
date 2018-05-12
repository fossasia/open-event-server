from app.models import db


class Permission(db.Model):
    """Role-Service Permissions
    """
    __tablename__ = 'permissions'
    __table_args__ = (db.UniqueConstraint('role_id', 'service_id', name='role_service_uc'),)

    id = db.Column(db.Integer, primary_key=True)

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'))
    role = db.relationship('Role')

    service_id = db.Column(db.Integer, db.ForeignKey('services.id', ondelete='CASCADE'))
    service = db.relationship('Service')

    can_create = db.Column(db.Boolean, nullable=False)
    can_read = db.Column(db.Boolean, nullable=False)
    can_update = db.Column(db.Boolean, nullable=False)
    can_delete = db.Column(db.Boolean, nullable=False)

    def __init__(self,
                 role,
                 service,
                 can_create=True,
                 can_read=True,
                 can_update=True,
                 can_delete=True):
        self.role = role
        self.service = service
        self.can_create = can_create
        self.can_read = can_read
        self.can_update = can_update
        self.can_delete = can_delete

    def __repr__(self):
        return '<Perm %r for %r>' % (self.role,
                                     self.service,)

    def __str__(self):
        return self.__repr__()

from app.models import db
from app.models.panel_permission import PanelPermission


class CustomSysRole(db.Model):
    """Custom System Role
    """
    __tablename__ = 'custom_sys_roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)

    def __init__(self, name):
        self.name = name

    def can_access(self, panel_name):
        panel = PanelPermission.query.filter_by(panel_name=panel_name).first()
        for role in panel.custom_system_roles:
            if role.id == self.id:
                return panel.can_access
        return False

    def __repr__(self):
        return '<CustomSysRole %r>' % self.name

    def __str__(self):
        return self.__repr__()


class UserSystemRole(db.Model):
    """User Custom System Role
    """
    __tablename__ = 'user_system_role'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id',
                                                  ondelete='CASCADE'))
    user = db.relationship('User')

    event_id = db.Column(db.Integer, db.ForeignKey('events.id',
                                                   ondelete='CASCADE'))
    event = db.relationship('Event')

    role_id = db.Column(db.Integer, db.ForeignKey('custom_sys_roles.id',
                                                  ondelete='CASCADE'))
    role = db.relationship('CustomSysRole')

    def __init__(self, user=None, event=None, role=None,
                 user_id=None, role_id=None, event_id=None):
        if user:
            self.user = user
        if event:
            self.event = event
        if role:
            self.role = role
        if user_id:
            self.user_id = user_id
        if role_id:
            self.role_id = role_id
        if event_id:
            self.event_id = event_id

    def __str__(self):
        return '%r as %r' % (self.user, self.role, self.event)

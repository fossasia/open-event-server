from app.models import db
from app.models.panel_permission import PanelPermission


class CustomSysRole(db.Model):
    """Custom System Role"""

    __tablename__ = 'custom_sys_roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)

    def can_access(self, panel_name):
        panel = PanelPermission.query.filter_by(panel_name=panel_name).first()
        for role in panel.custom_system_roles:
            if role.id == self.id:
                return panel.can_access
        return False

    def __repr__(self):
        return '<CustomSysRole %r>' % self.name


class UserSystemRole(db.Model):
    """User Custom System Role"""

    __tablename__ = 'user_system_role'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    user = db.relationship('User')

    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    event = db.relationship('Event')

    role_id = db.Column(
        db.Integer, db.ForeignKey('custom_sys_roles.id', ondelete='CASCADE')
    )
    role = db.relationship('CustomSysRole')

    def __repr__(self):
        return f'{self.user!r} as {self.role!r}'

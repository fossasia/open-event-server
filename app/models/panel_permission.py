from app.models import db


class PanelPermission(db.Model):
    """Super-Admin Panel Permissions
    """
    __tablename__ = 'panel_permissions'

    id = db.Column(db.Integer, primary_key=True)
    # Super Admin panel name
    panel_name = db.Column(db.String)
    # Custom System Role
    role_id = db.Column(db.Integer, db.ForeignKey('custom_sys_roles.id',  ondelete='CASCADE'))
    role = db.relationship('CustomSysRole')

    can_access = db.Column(db.Boolean)

    def __init__(self, panel_name, role, can_access=True):
        self.panel_name = panel_name
        self.role = role
        self.can_access = can_access

    def __repr__(self):
        return '<PanelPerm %r for %r>' % (self.role, self.panel_name)

    def __str__(self):
        return self.__repr__()

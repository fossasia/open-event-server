from app.models import db


roles_panels = db.Table('roles_panels',
                        db.Column('role_id', db.Integer, db.ForeignKey('custom_sys_roles.id', ondelete='CASCADE')),
                        db.Column('panel_permission_id', db.Integer,
                                  db.ForeignKey('panel_permissions.id', ondelete='CASCADE')))


class PanelPermission(db.Model):
    """Super-Admin Panel Permissions
    """
    __tablename__ = 'panel_permissions'

    id = db.Column(db.Integer, primary_key=True)
    # Super Admin panel name
    panel_name = db.Column(db.String)
    # Custom System Role
    roles = db.relationship('CustomSysRole',
                            secondary=roles_panels,
                            backref=db.backref('panels', lazy='dynamic'))

    can_access = db.Column(db.Boolean)

    def __init__(self, panel_name, roles=None, can_access=True):
        self.panel_name = panel_name
        if roles is None:
            self.roles = []
        else:
            self.roles = roles
        self.can_access = can_access

    def __repr__(self):
        return '<PanelPerm %r for %r>' % (self.role, self.panel_name)

    def __str__(self):
        return self.__repr__()

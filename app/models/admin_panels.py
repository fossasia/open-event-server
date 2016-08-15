from . import db


class PanelPermission(db.Model):
    """Super-Admin Panel Permissions
    """
    __tablename__ = 'panel_permissions'

    id = db.Column(db.Integer, primary_key=True)
    # Super Admin panel name
    panel_name = db.Column(db.String)
    # System-Role
    role_name = db.Column(db.String)

    can_access = db.Column(db.Boolean)

    def __init__(self, panel_name, role_name, can_access=True):
        self.panel_name = panel_name
        self.role_name = role_name
        self.can_access = can_access

    def __repr__(self):
        return '<PanelPerm %r for %r>' % (self.role_name, self.panel_name)

    def __unicode__(self):
        return 'PanelPerm %r for %r' % (self.role_name, self.panel_name)

    def __str__(self):
        return unicode(self).encode('utf-8')

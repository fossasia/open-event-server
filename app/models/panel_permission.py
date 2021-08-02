from app.models import db

roles_panels = db.Table(
    'roles_panels',
    db.Column(
        'role_id',
        db.Integer,
        db.ForeignKey('custom_sys_roles.id', ondelete='CASCADE'),
        nullable=False,
    ),
    db.Column(
        'panel_permission_id',
        db.Integer,
        db.ForeignKey('panel_permissions.id', ondelete='CASCADE'),
        nullable=False,
    ),
)


class PanelPermission(db.Model):
    """Super-Admin Panel Permissions"""

    __tablename__ = 'panel_permissions'

    id = db.Column(db.Integer, primary_key=True)
    # Super Admin panel name
    panel_name = db.Column(db.String)
    # Custom System Role
    custom_system_roles = db.relationship(
        'CustomSysRole',
        secondary=roles_panels,
        backref=db.backref('panel_permissions', lazy='dynamic'),
    )

    can_access = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return '<PanelPerm {!r} for {!r}>'.format(
            self.custom_system_roles, self.panel_name
        )

from . import db


class CustomSysRole(db.Model):
    """Custom System Role
    """
    __tablename__ = 'custom_sys_role'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    title = db.Column(db.String)

    def __init__(self, name, title):
        self.name = name
        self.title = title

    def __repr__(self):
        return '<CustomSysRole %r>' % self.name

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.name

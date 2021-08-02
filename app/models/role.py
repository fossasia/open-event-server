from app.models import db


class Role(db.Model):
    """Event Role"""

    __tablename__ = 'roles'

    OWNER = 'owner'
    ORGANIZER = 'organizer'
    COORGANIZER = 'coorganizer'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    title_name = db.Column(db.String)

    def __repr__(self):
        return '<Role %r>' % self.name

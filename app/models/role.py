from app.models import db
from app.models.base import SoftDeletionModel


class Role(SoftDeletionModel):
    """Event Role
    """

    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    title_name = db.Column(db.String)

    def __repr__(self):
        return '<Role %r>' % self.name

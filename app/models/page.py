from app.models import db


class Page(db.Model):
    """Page model class"""

    __tablename__ = 'pages'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    title = db.Column(db.String)
    url = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    place = db.Column(db.String)
    language = db.Column(db.String)
    index = db.Column(db.Integer, default=0)

    def __repr__(self):
        return '<Page %r>' % self.name

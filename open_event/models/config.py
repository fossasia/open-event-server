from . import db
class Config(db.Model):
    __tablename__ = 'configs'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    logo = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    color = db.Column(db.String, nullable=False)


    def __init__(self, title=None, logo=None, email=None, color=None ):
        self.title = title
        self.logo = logo
        self.email = email
        self.color = color

    def __repr__(self):
        return '<Config %r>' % (self.title)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'title': self.title,
                'logo': self.logo,
                'email': self.email,
                'color': self.color
                }

"""Copyright 2015 Rafal Kowalski"""
from . import db


class Speaker(db.Model):
    """Speaker model class"""
    __tablename__ = 'speaker'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    photo = db.Column(db.String)
    biography = db.Column(db.Text)
    email = db.Column(db.String, nullable=False)
    web = db.Column(db.String)
    twitter = db.Column(db.String)
    facebook = db.Column(db.String)
    github = db.Column(db.String)
    linkedin = db.Column(db.String)
    organisation = db.Column(db.String, nullable=False)
    position = db.Column(db.String)
    country = db.Column(db.String, nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))

    def __init__(self,
                 name=None,
                 photo=None,
                 biography=None,
                 email=None,
                 web=None,
                 twitter=None,
                 facebook=None,
                 github=None,
                 linkedin=None,
                 organisation=None,
                 position=None,
                 country=None,
                 event_id=None):
        self.name = name
        self.photo = photo
        self.biography = biography
        self.email = email
        self.web = web
        self.twitter = twitter
        self.facebook = facebook
        self.github = github
        self.linkedin = linkedin
        self.organisation = organisation
        self.position = position
        self.country = country
        self.event_id = event_id

    def __repr__(self):
        return '<Speaker %r>' % (self.name)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""

        session_data = [{'title': session.title, 'id': session.id} for session in self.sessions]

        return {'id': self.id,
                'name': self.name,
                'photo': self.photo,
                'biography': self.biography,
                'email': self.email,
                'web': self.web,
                'twitter': self.twitter,
                'facebook': self.facebook,
                'github': self.github,
                'linkedin': self.linkedin,
                'organisation': self.organisation,
                'position': self.position,
                'country': self.country,
                'sessions': session_data}
